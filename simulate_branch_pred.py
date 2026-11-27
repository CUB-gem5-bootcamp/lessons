from gem5.components.boards.riscv_board import RiscvBoard
from gem5.components.cachehierarchies.classic.private_l1_shared_l2_cache_hierarchy import PrivateL1SharedL2CacheHierarchy
from gem5.components.memory.single_channel import SingleChannelDDR4_2400
from gem5.resources.resource import obtain_resource
from gem5.simulate.simulator import Simulator

from m5.objects.BranchPredictor import BranchPredictor
from m5.debug import flags

from branch_pred_processor import BranchPredProcessor
from m5.objects import CustomGshare

processor = BranchPredProcessor(
  branch_predictor = CustomGshare(tableEntries=4096, historyBits=12,)
)

cache = PrivateL1SharedL2CacheHierarchy(
    l1d_size = "16KiB",
    l1i_size = "16KiB",
    l2_size = "256KiB",
    l1d_assoc = 8,
    l1i_assoc = 8,
    l2_assoc = 16
)

memory = SingleChannelDDR4_2400(
    size = "3GiB"
)

board = RiscvBoard(
    clk_freq="3GHz",
    processor = processor,
    cache_hierarchy = cache,
    memory = memory
)

board.set_se_binary_workload(
    binary = obtain_resource("riscv-cce")
)

sim = Simulator(board)
sim.schedule_max_insts(10_000_000)
sim.run()
