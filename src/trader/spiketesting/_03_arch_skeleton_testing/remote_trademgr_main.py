
from spiketesting._03_arch_skeleton_testing.trademgr.itrademgr import ITradeMgr
from spiketesting._03_arch_skeleton_testing.trademgr.remote_trademgr import RemoteTradeMgr

if __name__ == '__main__':
    trade_mgr = RemoteTradeMgr()
    trade_mgr.start_trading()