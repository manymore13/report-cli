#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
研报命令行工具
支持查询和下载行业研报、个股研报、策略报告、宏观研究、券商晨报
"""

import argparse
import os
import sys
from datetime import datetime

from . import report_client


def create_parser():
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        description='report v1.3.2 --查询和下载券商研报',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
命令
  report q     查询研报 (只查看列表，不下载文件)
  report d     下载研报 PDF (仅用户明确说"下载"才用)
  report l     列出所有行业
  report u     更新行业列表

查询示例
  report q -i 1046                    查询游戏行业研报
  report q -i 1046 -s 10              查询10条
  report q -t stock -c 600519         查询茅台个股研报
  report q -t strategy -s 5           查询策略报告
  report q -t macro                   查询宏观研究
  report q -t morning                 查询券商晨报
  report q -i 1046 --begin 2025-06-01 --end 2025-12-31   按日期筛选
  report q -i 1046 --save-csv         查询并导出CSV

下载示例
  report d -i 1046 -o ./reports       下载游戏行业研报
  report d -i 1046 -s 3               下载3篇
  report d -t stock -c 600519 -o ./mt 下载茅台研报

行业列表
  report l                            列出所有行业
  report l -s 游戏                    搜索包含"游戏"的行业

更新
  report u                            更新行业数据

上报类型: industry(行业) | stock(个股) | strategy(策略) | macro(宏观) | morning(晨报)
        '''
    )
    
    # 添加子命令
    # 设置 prog 为 report.py 以便显示正确的命令名
    subparsers = parser.add_subparsers(dest='command', help='可用命令 (输入 help 查看详情)', prog='report')

    # ==================== query 命令 ====================
    parser_query = subparsers.add_parser(
        'query',
        aliases=['q'],
        help='查询研报列表 (只查看，不下载文件)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
用法示例

  # 查询行业研报 (默认类型)
  report q -i 1046                    游戏行业
  report q -i 1046 -s 10              游戏行业，10条
  report q -i 1046 -p 2 -s 10         游戏行业，第2页

  # 查询个股研报
  report q -t stock -c 600519         贵州茅台
  report q -t stock -c 000001         平安银行

  # 查询其他类型
  report q -t strategy -s 5           策略报告
  report q -t macro                   宏观研究
  report q -t morning                 券商晨报

  # 按日期筛选
  report q -i 1046 --begin 2025-06-01 --end 2025-12-31

  # 导出CSV
  report q -i 1046 --save-csv         保存到当前目录
  report q -i 1046 -o ./data --save-csv  保存到指定目录

参数说明
  -t, --type      研报类型，可选值见下方。不指定默认为 industry
                  industry = 行业研报 (需要 -i 行业代码)
                  stock    = 个股研报 (需要 -c 股票代码)
                  strategy = 策略报告
                  macro    = 宏观研究
                  morning  = 券商晨报

  -i, --industry  行业代码，如 1046=游戏, 1036=半导体, 1033=电池
                  先用 report l 查看所有行业及代码

  -c, --code      股票代码，如 600519=贵州茅台, 000001=平安银行

  -p, --page      页码，从第1页开始。默认: 1

  -s, --pagesize  每页返回条数。默认: 20

  --begin         开始日期，格式 YYYY-MM-DD，如 2025-01-01
  --end           结束日期，格式 YYYY-MM-DD，如 2025-12-31

  -o, --output    CSV文件输出目录 (需配合 --save-csv 使用)

  --save-csv      将查询结果保存为CSV文件，可用Excel打开
        '''
    )
    parser_query.add_argument(
        '-t', '--type',
        type=str,
        choices=['industry', 'stock', 'strategy', 'macro', 'morning'],
        default='industry',
        help='研报类型: industry(行业) | stock(个股) | strategy(策略) | macro(宏观) | morning(晨报) 默认: industry'
    )
    parser_query.add_argument(
        '-i', '--industry',
        type=str,
        help='行业代码，如 1046=游戏, 1036=半导体。用 report l 查看所有行业'
    )
    parser_query.add_argument(
        '-c', '--code',
        type=str,
        help='股票代码，如 600519=贵州茅台, 000001=平安银行'
    )
    parser_query.add_argument(
        '-p', '--page',
        type=int,
        default=1,
        help='页码，从1开始。默认: 1'
    )
    parser_query.add_argument(
        '-s', '--pagesize',
        type=int,
        default=20,
        help='每页数量。默认: 20'
    )
    parser_query.add_argument(
        '--begin',
        type=str,
        help='开始日期，格式 YYYY-MM-DD，如 2025-01-01'
    )
    parser_query.add_argument(
        '--end',
        type=str,
        help='结束日期，格式 YYYY-MM-DD，如 2025-12-31'
    )
    parser_query.add_argument(
        '-o', '--output',
        type=str,
        help='CSV文件输出目录，需配合 --save-csv 使用'
    )
    parser_query.add_argument(
        '--save-csv',
        action='store_true',
        help='将查询结果保存为CSV文件，可用Excel打开'
    )
    
    # ==================== download 命令 ====================
    parser_download = subparsers.add_parser(
        'download',
        aliases=['d'],
        help='下载研报 PDF (仅用户明确说"下载"时才用)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
用法示例

  # 下载行业研报
  report d -i 1046 -o ./reports      游戏行业，保存到 ./reports
  report d -i 1046 -s 5              游戏行业，5篇
  report d -i 1046 -s 3 -p 2        游戏行业，第2页，3篇
  report d -i 1046 -s 5 -n 5        查询5篇，只下载第5篇
  report d -i 1046 -n 1,3,5         只下载第1、3、5篇

  # 下载个股研报
  report d -t stock -c 600519 -o ./mt   茅台研报

  # 下载其他类型
  report d -t strategy -s 5 -o ./reports  策略报告
  report d -t macro -s 5 -o ./reports     宏观研究

  # 按日期筛选下载
  report d -i 1046 --begin 2025-06-01 --end 2025-12-31 -o ./reports

参数说明
  -t, --type      研报类型，默认: industry
                  industry = 行业研报 (需要 -i 行业代码)
                  stock    = 个股研报 (需要 -c 股票代码)
                  strategy = 策略报告
                  macro    = 宏观研究
                  morning  = 券商晨报

  -i, --industry  行业代码，如 1046=游戏, 1036=半导体
                  先用 report l 查看所有行业及代码

  -c, --code      股票代码，如 600519=贵州茅台

  -p, --page      下载第几页，默认: 1

  -s, --pagesize  每页下载数量，默认: 20

  -n, --index     指定下载第几条 (1-based)。如 -n 5 只下载第5篇
                  支持逗号分隔多个: -n 1,3,5 下载第1、3、5篇
                  不指定则下载全部

  -o, --output    输出目录，PDF 保存位置。默认: ./reports
                  下载后会按类型创建子目录，如 ./reports/industry/

  --begin         开始日期，格式 YYYY-MM-DD
  --end           结束日期，格式 YYYY-MM-DD

  --all           下载该类型所有可用的研报 (注意: 数量可能很大)
        '''
    )
    parser_download.add_argument(
        '-t', '--type',
        type=str,
        choices=['industry', 'stock', 'strategy', 'macro', 'morning'],
        default='industry',
        help='研报类型。默认: industry'
    )
    parser_download.add_argument(
        '-i', '--industry',
        type=str,
        help='行业代码，如 1046=游戏'
    )
    parser_download.add_argument(
        '-c', '--code',
        type=str,
        help='股票代码，如 600519=贵州茅台'
    )
    parser_download.add_argument(
        '-p', '--page',
        type=int,
        default=1,
        help='页码。默认: 1'
    )
    parser_download.add_argument(
        '-s', '--pagesize',
        type=int,
        default=20,
        help='每页数量。默认: 20'
    )
    parser_download.add_argument(
        '-o', '--output',
        type=str,
        default='./reports',
        help='输出目录，PDF存放位置。默认: ./reports'
    )
    parser_download.add_argument(
        '--begin',
        type=str,
        help='开始日期，格式 YYYY-MM-DD'
    )
    parser_download.add_argument(
        '--end',
        type=str,
        help='结束日期，格式 YYYY-MM-DD'
    )
    parser_download.add_argument(
        '-n', '--index',
        type=str,
        help='指定下载第几条，如 5 或 1,3,5。不指定则下载全部'
    )
    parser_download.add_argument(
        '--all',
        action='store_true',
        help='下载该类型所有可用的研报'
    )

    # ==================== list 命令 ====================
    parser_list = subparsers.add_parser(
        'list',
        aliases=['l'],
        help='列出所有行业及代码',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
用法示例

  report l               列出所有行业及代码
  report l -s 游戏       搜索包含"游戏"的行业
  report l -s 半导体      搜索包含"半导体"的行业

参数说明
  -s, --search   关键词，模糊匹配行业名称。不指定则列出全部
        '''
    )
    parser_list.add_argument(
        '-s', '--search',
        type=str,
        help='按关键词搜索行业名称，如 游戏、半导体、银行'
    )

    # ==================== update 命令 ====================
    parser_update = subparsers.add_parser(
        'update',
        aliases=['u'],
        help='从数据源更新行业列表',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
用法示例

  report u               更新行业列表到最新

说明
  当行业分类有变化或新增行业时，运行此命令同步最新数据。
  无需任何参数，直接运行即可。
        '''
    )
    
    return parser


def parse_args(args=None):
    """解析命令行参数"""
    parser = create_parser()
    parsed = parser.parse_args(args)
    
    # 验证参数组合
    if parsed.command == 'query':
        if parsed.type == 'industry' and not parsed.industry:
            parser.error('错误: 行业研报需要指定行业代码 (-i 参数)\n   用法: py -3 -m eastmoney q -i 1046')
        if parsed.type == 'stock' and not parsed.code:
            parser.error('错误: 个股研报需要指定股票代码 (-c 参数)\n   用法: py -3 -m eastmoney q -c 600519')
        if parsed.type in ['strategy', 'macro', 'morning'] and parsed.industry:
            parser.error(f'错误: {parsed.type} 类型不需要指定行业代码')
            
    elif parsed.command == 'download':
        if parsed.type == 'industry' and not parsed.industry and not parsed.all:
            parser.error('错误: 下载行业研报需要指定行业代码 (-i) 或使用 --all 参数')
        if parsed.type == 'stock' and not parsed.code:
            parser.error('错误: 下载个股研报需要指定股票代码 (-c 参数)\n   用法: py -3 -m eastmoney d -c 600519 -o ./reports')
    
    return parsed


def validate_date(date_str, parser):
    """验证日期格式"""
    if not date_str:
        return None
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return date_str
    except ValueError:
        parser.error(f'错误: 日期格式错误 {date_str}，请使用 YYYY-MM-DD 格式')


# ==================== CLI Command Handlers ====================

def parse_index(index_str, total):
    """Parse --index argument like '5' or '1,3,5', return list of 0-based indexes"""
    result = []
    for part in index_str.split(','):
        part = part.strip()
        if '-' in part:
            a, b = part.split('-', 1)
            result.extend(range(int(a) - 1, int(b)))
        else:
            result.append(int(part) - 1)
    return [i for i in result if 0 <= i < total]


def handle_query(args):
    """Handle query command"""
    client = report_client.EastMoneyReportClient()
    
    data = client.fetch_reports(
        report_type=args.type,
        industry_code=args.industry,
        stock_code=args.code,
        page_no=args.page,
        page_size=args.pagesize,
        begin_time=args.begin,
        end_time=args.end
    )
    
    if not data:
        print('获取研报数据失败')
        return
    
    reports = client.parse_reports(data, report_type=args.type)
    
    if not reports:
        print('未找到研报')
        return
    
    client.display_reports(reports, page_no=args.page)
    
    if args.output or args.save_csv:
        if args.type == 'industry':
            type_name = client.get_industry_name(args.industry) or args.industry
        elif args.type == 'stock':
            type_name = args.code
        else:
            type_name = args.type
        
        filename = args.output or '.'
        if not args.output:
            filename = os.path.join('.', f'{type_name}_reports.csv')
        else:
            filename = os.path.join(args.output, f'{type_name}_page{args.page}.csv')
        
        client.save_reports_to_csv(reports, filename)


def handle_download(args):
    """Handle download command"""
    client = report_client.EastMoneyReportClient(output_dir=args.output)
    
    if args.all and args.type == 'industry':
        industries = client.get_industry_list()
        print(f'开始下载所有行业研报，共 {len(industries)} 个行业...')
        
        for idx, industry in enumerate(industries, 1):
            print(f'\n[{idx}/{len(industries)}] 正在下载: {industry["industry_name"]}...')
            
            data = client.fetch_reports(
                report_type=args.type,
                industry_code=industry['industry_code'],
                page_no=args.page,
                page_size=args.pagesize,
                begin_time=args.begin,
                end_time=args.end
            )
            
            if data:
                reports = client.parse_reports(data, report_type=args.type)
                if reports:
                    client.download_reports(reports, args.output, report_type=industry['industry_name'])
    else:
        data = client.fetch_reports(
            report_type=args.type,
            industry_code=args.industry,
            stock_code=args.code,
            page_no=args.page,
            page_size=args.pagesize,
            begin_time=args.begin,
            end_time=args.end
        )
        
        if not data:
            print('获取研报数据失败')
            return
        
        reports = client.parse_reports(data, report_type=args.type)
        
        if not reports:
            print('未找到研报')
            return
        
        client.display_reports(reports, page_no=args.page)

        # 如果指定了 --index，只下载对应序号的报告
        if args.index:
            indexes = parse_index(args.index, len(reports))
            reports = [reports[i] for i in indexes]
            print(f'指定下载第 {args.index} 篇')

        type_name = args.type
        if args.type == 'industry' and args.industry:
            type_name = client.get_industry_name(args.industry) or args.industry
        elif args.type == 'stock' and args.code:
            type_name = args.code

        client.download_reports(reports, args.output, report_type=type_name)


def handle_list(args):
    """Handle list command"""
    client = report_client.EastMoneyReportClient()
    
    industries = client.search_industry(args.search)
    
    if not industries:
        print('未找到匹配的行业')
        return
    
    print(f'\n{"="*60}')
    print(f'{"行业代码":<15} {"行业名称":<30} {"页大小":<10}')
    print(f'{"="*60}')
    
    for industry in industries:
        code = industry.get('industry_code', '')
        name = industry.get('industry_name', '')
        size = industry.get('page_size', '')
        print(f'{code:<15} {name:<30} {size:<10}')
    
    print(f'{"="*60}')
    print(f'共 {len(industries)} 个行业\n')


def handle_update(args):
    """Handle update command"""
    client = report_client.EastMoneyReportClient()
    client.update_industry_data()


def main():
    """Main entry point"""
    args = parse_args()
    
    if not args.command:
        create_parser().print_help()
        return
    
    command_map = {
        'q': 'query',
        'query': 'query',
        'd': 'download',
        'download': 'download',
        'l': 'list',
        'list': 'list'
    }
    
    cmd = command_map.get(args.command, args.command)
    
    if cmd == 'query':
        handle_query(args)
    elif cmd == 'download':
        handle_download(args)
    elif cmd == 'list':
        handle_list(args)
    elif cmd == 'update':
        handle_update(args)


if __name__ == '__main__':
    main()
