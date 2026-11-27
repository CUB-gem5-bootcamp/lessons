#include "cpu/pred/custom_gshare.hh"
#include <algorithm>

namespace gem5 
{

namespace branch_prediction
{


CustomGshare::CustomGshare(const CustomGshareParams &params):
    ConditionalPredictor(params),
    counters(params.tableEntries, 1),
    globalHistory(params.numThreads, 0),
    historyBits(params.historyBits)
{}

Prediction 
CustomGshare::lookup(ThreadID tid, Addr pc, void *&bp_history) 
{
    auto idx = ((pc >> instShiftAmt) ^ globalHistory[tid])
               & (counters.size() - 1);
    bool taken = counters[idx] >= 2;
    bp_history = new History{globalHistory[tid], idx, taken};
    globalHistory[tid] = ((globalHistory[tid] << 1) | taken);
    return predictWithDefaultLatency(taken);
}

void 
CustomGshare::update(ThreadID tid, Addr pc, bool taken, void * &bp_history, 
                    bool squashed, const StaticInstPtr &inst, Addr target) 
{
    // Return immediately if history is null
    if (bp_history == nullptr) {
        return;
    }

    auto *h = static_cast<History *>(bp_history);
    auto &ctr = counters[h->index];

    if (squashed) {
        // If squashed, change global history to account misprediction
        globalHistory[tid] = ((h->oldGhr << 1) | taken);
    } else {
        // Else, shift counter and free history
        if (taken) ctr = std::min(3, int(ctr) + 1);
        else       ctr = std::max(0, int(ctr) - 1);
        delete h;
        bp_history = nullptr;
    }
}

void
CustomGshare::squash(ThreadID tid, void * &bp_history)
{
    // Return immediately if history is null
    if (bp_history == nullptr) {
        return;
    }

    auto *h = static_cast<History *>(bp_history);
    globalHistory[tid] = h->oldGhr;
    delete h;
    bp_history = nullptr;

}
} // branch_prediction
} // gem5


// On a misprediction, restore the checkpoint and then
// shift in the RESOLVED direction if required by API.
