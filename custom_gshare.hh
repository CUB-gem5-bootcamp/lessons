#ifndef __CPU_PRED_CUSTOM_GSHARE_HH__
#define __CPU_PRED_CUSTOM_GSHARE_HH__

#include "arch/generic/pcstate.hh"
#include "cpu/inst_seq.hh"
#include "cpu/pred/branch_type.hh"
#include "sim/clocked_object.hh"
#include "params/CustomGshare.hh"
#include "cpu/pred/conditional.hh"
#include <vector>
#include <cstdint>

namespace gem5
{

namespace branch_prediction
{

class CustomGshare : public ConditionalPredictor 
{
  private:
    std::vector<uint8_t> counters;
    std::vector<uint64_t> globalHistory; // per thread
    unsigned historyBits;

    struct History {
      uint64_t oldGhr;
      unsigned index;
      bool prediction;
    };

  public:
    typedef CustomGshareParams Params;
    CustomGshare(const CustomGshareParams &params);
    
    Prediction lookup(ThreadID tid, Addr pc, void *&bp_history) override;

    void squash(ThreadID tid, void * &bp_history) override;

    void update(ThreadID tid, Addr pc, bool taken, void * &bp_history, bool squashed,
                const StaticInstPtr &inst, Addr target) override;

    void updateHistories(ThreadID tid, Addr pc, bool uncond, bool taken, Addr target,
                        const StaticInstPtr &inst, void * &bp_history) override {}

};

} // branch_predictor
} // gem5

#endif // __CPU_PRED_CUSTOM_GSHARE_HH__