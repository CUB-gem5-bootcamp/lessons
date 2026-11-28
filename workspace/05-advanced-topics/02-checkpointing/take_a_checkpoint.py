# Copyright (c) 2024 The Regents of the University of California.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met: redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer;
# redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution;
# neither the name of the copyright holders nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""

Usage:
------
gem5 -re 03-take-a-checkpoint.py
"""


from gem5.components.boards.x86_board import X86Board
from gem5.components.processors.cpu_types import CPUTypes
from gem5.components.processors.simple_processor import SimpleProcessor
from gem5.isas import ISA
from gem5.resources.resource import obtain_resource
from gem5.simulate.simulator import (
    ExitEvent,
    Simulator,
)
from gem5.utils.requires import requires
from gem5.simulate.exit_handler import register_exit_handler
from gem5.components.cachehierarchies.classic.no_cache import NoCache
from gem5.components.memory.single_channel import SingleChannelDDR4_2400
import m5
from pathlib import Path
from gem5.resources.resource import BinaryResource

requires(
    isa_required=ISA.X86,
    kvm_required=False,
)

# TODO (1): Set up a simple system configuration.

# Let's set up a NoCache cache hierarchy
# Note the needed import! (NoCache)
cache_hierarchy = NoCache()  

# Let's set up a SingleChannelDDR4_2400 memory with 3GiB size
# Also note the needed import! (SingleChannelDDR4_2400)
memory = SingleChannelDDR4_2400(size="3GiB") 

# Here we set up a simple processor with the KVM CPU
processor = SimpleProcessor(
    cpu_type=CPUTypes.ATOMIC,
    isa=ISA.X86, # For example
    num_cores=2,
)

board = X86Board(
    clk_freq="3GHz",
    processor=processor,
    memory=memory,
    cache_hierarchy=cache_hierarchy,
)

# Setting up a small workload for us to use, but you can also download a workload
binary_path = Path("annotated_workload")
board.set_se_binary_workload(
    binary = BinaryResource(
        local_path=binary_path.as_posix()
    )
)

# TODO (2): Set up workbegin handler to save a checkpoint and exit
def workbegin_handler(simulator, payload):
    print("Done booting Linux")

    print("Take a checkpoint")
    simulator.save_checkpoint("03-cpt") # This will be the saved checkpoint's directory name

    return True

# Thank you, hypercalls! 
register_exit_handler(4,workbegin_handler,"hello, checkpointing!")

simulator = Simulator(
    board=board,
)

print("Running the simulation")

simulator.run()

print("Simulation Done")
