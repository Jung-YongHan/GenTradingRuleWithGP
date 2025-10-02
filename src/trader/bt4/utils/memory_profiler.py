import tracemalloc
import os
import psutil

class MemoryProfiler:

    def __init__(self):
        self.snapshot = None
        tracemalloc.start()

    ##########################################################################
    ## Methods for comparing memory difference between two snapshots.
    def take_1st_snapshot(self):
        self.snapshot = tracemalloc.take_snapshot()

    def take_2nd_snapshot_and_show_topN(self, n = 10, terminate=False):
        if self.snapshot == None:
            print(f"Top {n} can be shown after calling 'take_snapshot()'.")
            return
        else:
            lines = []
            # 현재 메모리 상태를 최초와 비교하여 얼마나 차이가 나는지에 대한 통계를 구한다
            top_stats = tracemalloc.take_snapshot().compare_to(self.snapshot, 'lineno')
            # 메모리 사용량이 많은 순서대로 10개를 구하여 출력한다
            print(f"MEMORY SNAPSHOT PROFILING.. "+"######"*5)
            for idx, stat in enumerate(top_stats[:n]) :
                lines.append(f"{idx}-> {str(stat)}")
            print('\n'.join(lines), flush = True)

        if terminate:
            pid = os.getpid()
            print(f'{pid} has been killed!')
            os.kill(pid, 2)

    ##########################################################################
    ## print current highest memory usage
    def show_top5_current_memory_usage(self, terminate=False):
        # 현재 메모리 상태에 대한 통계를 생성하고 사용량이 많은 순서대로 5개 결과를 출력한다
        snapshot = tracemalloc.take_snapshot()
        print(f"MEMORY USAGE PROFILING.. " + "######" * 5)
        for idx, stat in enumerate(snapshot.statistics('lineno')[:5], 1) :
            print(f"{idx}-> {str(stat)}", flush = True)
        # 메모리 사용량이 가장 많은 부분에 대한 정보를 상세히 출력한다
        traces = tracemalloc.take_snapshot().statistics('traceback')
        for stat in traces[:1] :
            print("memory_blocks=", stat.count, "size_kB=", stat.size / 1024, flush = True)
            for line in stat.traceback.format() :
                print(line, flush = True)

        if terminate:
            pid = os.getpid()
            print(f'{pid} has been killed!')
            os.kill(pid, 2)

    def print_mem_usage(self):
        print("Process Memory Used(MB):" + str(self.get_mem_usage()))

    def get_mem_usage(self):
        return psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2

    def keep_1st_mem_usage(self):
        self.memory_before_read = psutil.Process().memory_info().rss / 1024 ** 2
        print("keep_1st_memory_usage(MB): ", self.memory_before_read)
        return self.memory_before_read

    def keep_2nd_mem_usage_calc_gap(self):
        memory_after_gc = psutil.Process().memory_info().rss / 1024 ** 2
        print("keep_2nd_memory_usage(MB): ", memory_after_gc)
        print("gap between 1st and 2nd(memory leak)(MB): ", memory_after_gc - self.memory_before_read)
        return memory_after_gc - self.memory_before_read



