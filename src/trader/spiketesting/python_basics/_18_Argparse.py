import argparse   	# 내장모듈
import sys

def main(start_mode,  config_name):
    print(f'start_mode : {start_mode}')
    print(f'config_name : {config_name}')

def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(nargs='?', help='start_mode: simulator or real_trading)', dest='start_mode')
    parser.add_argument('-conf', nargs='?', help='configuration name', dest='config_name')

    # parser.add_argument(nargs='+' ,help='Example) index.html', dest='filename')
    # parser.add_argument('--optional', '-o', nargs='*', help='Example) save', default=[], dest='option')
    # filename_list = parser.parse_args().filename
    # option_list = parser.parse_args().option
    # return filename_list, option_list

    start_mode = parser.parse_args().start_mode
    # module_name = parser.parse_args().module_name
    # strategy_name = parser.parse_args().strategy_name
    config_name = parser.parse_args().config_name

    return start_mode, config_name


# def get_arguments():
#     parser = argparse.ArgumentParser()
#     parser.add_argument(nargs='?', help='start_mode: simulator or real_trading)', dest='start_mode')
#     parser.add_argument('-conf', nargs='?', help='configuration name (.py)', dest='config_name')

if __name__ == '__main__':
    sys.argv = ['me', 'simulator' ,'-conf', '.\conf\winning_session_vol_02_period_5']
    start_mode, config_name = get_arguments()
    main(start_mode, config_name)