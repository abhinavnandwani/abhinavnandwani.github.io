# RLVR GPU training costs, benchmarks, and pricing

**Reinforcement Learning from Verifiable Rewards (RLVR) has emerged as the dominant paradigm for training reasoning models, yet published throughput data remains sparse and concentrated on 7B-scale models.** The best measured GRPO throughput on an H100 SXM is **1,544 tokens/GPU/second** for a 7B model at 1K response length — roughly **1.7–2.5× faster than PPO-based RLHF** due to eliminating the critic model. However, RLVR's characteristic long chain-of-thought rollouts (8K–32K tokens) create a massive generation bottleneck that consumes **70–90% of total wall-clock time**, making it approximately **5–10× slower than supervised fine-tuning**. Cloud GPU costs for RLVR training range from **$0.29 to $1.11 per million tokens** at 7B scale depending on GPU type and provider, with MI300X offering the best price-performance at current market rates. Published training runs span five orders of magnitude in cost — from $2.62 for a 2B visual reasoning model to ~$200K for DeepSeek-R1-Zero's 671B MoE GRPO training.

---

## Measured RLVR throughput reveals GRPO's efficiency advantage

The only published tokens/GPU/second benchmarks for RLVR training come from the AMD ROCm blog (April 2025) using veRL v0.3.0 on GSM8K, with additional data from Yotta Labs and framework comparison papers. All measured data is concentrated on **7B-parameter models** — no comparable benchmarks exist for 14B, 32B, or 70B models in standardized tokens/GPU/sec format.

| GPU | Model | Algorithm | TP | Tokens/GPU/sec | Response Length | Framework | Source |
|-----|-------|-----------|----|---------------|-----------------|-----------|--------|
| H100 SXM | Qwen2-7B | **GRPO** | 2 | **1,544** | 1,024 | veRL v0.3 | AMD ROCm Blog |
| MI300X | Qwen2-7B | **GRPO** | 2 | **1,748** | 1,024 | veRL v0.3 | AMD ROCm Blog |
| H100 SXM | DeepSeek-7B | **GRPO** | 2 | **1,624** | 1,024 | veRL v0.3 | AMD ROCm Blog |
| MI300X | DeepSeek-7B | **GRPO** | 2 | **1,899** | 1,024 | veRL v0.3 | AMD ROCm Blog |
| H100 SXM | Qwen2-7B | PPO | 2 | 907 | 512 | veRL v0.3 | AMD ROCm Blog |
| MI300X | Qwen2-7B | PPO | 2 | 921 | 512 | veRL v0.3 | AMD ROCm Blog |
| H100 SXM | DeepSeek-7B | PPO | 4 | 624 | 512 | veRL v0.3 | AMD ROCm Blog |
| MI300X | DeepSeek-7B | PPO | 4 | 767 | 512 | veRL v0.3 | AMD ROCm Blog |

These benchmarks used 8 GPUs per node with train_batch_size=1024. Two critical patterns emerge: **GRPO achieves 1.7–2.5× higher throughput than PPO** because it eliminates the critic model entirely, and **MI300X outperforms H100 by 1–23%** across all configurations, likely due to its larger 192GB HBM3 memory enabling more efficient batching. Yotta Labs separately confirmed MI300X efficiency with veRL v0.5.0, achieving **14.01% training MFU** for 7B GRPO with optimal TP=1 on a single MI300X, and near-linear scaling across data parallelism dimensions.

The OpenRLHF paper provides a framework-level comparison: OpenRLHF completes one GSM8K GRPO epoch in **1,657 seconds** versus TRL's **5,189 seconds** — a **3.1× speedup** — on identical hardware and hyperparameters.

---

## Estimated throughput across model sizes requires significant extrapolation

Published RLVR throughput data is almost exclusively at 7B scale. The estimates below combine the measured 7B baselines with vLLM inference throughput scaling data (7B: ~6,300 tok/s → 32B: ~1,200 tok/s on a single H100, a **~5.25× drop**), the GPTOSS-20B MoE training benchmark (~500–598 tok/s on 512 H800 GPUs with veRL+Megatron), and the OLMo 3 32B RL training disclosure showing inference-to-training compute ratios of 5–14×.

| Model Size | H100 SXM (tok/GPU/s) | MI300X (tok/GPU/s) | A100 80GB (tok/GPU/s) | Confidence | Basis |
|-----------|----------------------|--------------------|-----------------------|------------|-------|
| 7B | **1,544–1,624** | **1,748–1,899** | ~900–1,100 | **Measured** | AMD ROCm Blog (veRL v0.3, GRPO, 1K resp.) |
| 14B | ~700–950 | ~800–1,100 | ~400–600 | Estimated | ~0.5–0.6× of 7B based on vLLM scaling |
| 32B | ~300–450 | ~350–520 | ~150–250 | Estimated | ~5.25× drop from 7B (vLLM data), GPTOSS-20B MoE ~500–598 tok/s on 512 GPUs |
| 70B | ~120–200 | ~140–240 | ~60–100 | Estimated | Requires multi-GPU TP; extrapolated from 32B |
| 235B-A22B (MoE) | ~200–350 | ~230–400 | N/A | Estimated | MoE with ~22B active params ≈ 32B-scale compute |
| 671B-A37B (MoE) | ~100–200 | ~120–250 | N/A | Estimated | Requires 96+ GPUs; EP+TP+PP parallelism |

**Critical caveat**: These estimates assume short (1K) response lengths matching the benchmark conditions. At RLVR-typical response lengths of 8K–32K tokens, overall step throughput stays roughly proportional (more tokens produced per step), but **each step takes 8–32× longer to complete** because autoregressive generation scales linearly with output length. KV cache pressure at longer contexts can also force batch size reductions, further degrading effective throughput. The QeRL paper notes that typical RL training for reasoning models takes **20–100 hours on 8× H100 GPUs** — suggesting effective throughput is significantly lower than these per-token rates imply when accounting for real-world RLVR conditions.

---

## Wall-clock training times from published RLVR runs

The table below compiles every published RLVR training run with disclosed compute details. Costs span from **$2.62 to ~$200,000**, driven primarily by model scale and rollout length.

| Run | Model | Size | Algorithm | GPUs | Wall-Clock | GPU-Hours | Est. Cost | Framework |
|-----|-------|------|-----------|------|-----------|-----------|-----------|-----------|
| DeepSeek-R1-Zero | DeepSeek-V3-Base | 671B MoE | GRPO | 512×H800 | ~198 hrs | **~101K** | ~$200K | Custom |
| DeepSeek-R1 (RL stage) | DeepSeek-V3-Base | 671B MoE | GRPO | 512×H800 | ~80 hrs | ~41K | ~$82K | Custom |
| ProRL-1.5B-v2 | — | 1.5B | RLVR | H100s | — | **>20K** | ~$60K+ | OpenRLHF |
| DAPO | Qwen2.5-32B | 32B | DAPO | 128×H20 | Several days | Not disclosed | — | veRL |
| SimpleRL-Zoo (32B) | Qwen2.5-32B | 32B | GRPO | 64×H100 | ~36 hrs | ~2,300 | ~$4,600 | veRL |
| Goldilocks RL | Various | — | GRPO | H100/B200 | — | ~1,000 | ~$2K–4K | — |
| DeepScaleR | R1-Distill-Qwen-1.5B | 1.5B | GRPO | 8–32×A100 | Multi-stage | 3,800 | **$4,500** | veRL |
| SimpleRL-Zoo (7B) | Qwen2.5-7B | 7B | GRPO | 16×H100 | ~15 hrs | ~240 | ~$500 | veRL |
| Dr. GRPO | Qwen2.5-Math-7B | 7B | Dr. GRPO | 8×A100 | ~27 hrs | ~216 | ~$430 | Oat |
| Sky-T1 (SFT, not RL) | Qwen2.5-32B-Instruct | 32B | SFT | 8×H100 | 19 hrs | 152 | **$450** | LlamaFactory |
| Open-R1 | Qwen2.5-Math-7B | 7B | GRPO | 8×H100 | ~3 hrs | 24 | ~$72 | TRL |
| Mini-R1 | Qwen2.5-3B-Instruct | 3B | GRPO | 4×H100 | ~6 hrs | 24 | ~$72 | TRL |
| microR1 | Qwen2.5-3B-Instruct | 3B | GRPO | 8×A100 | ~3 hrs | 24 | $44 | Pure PyTorch |
| TinyZero | Qwen2.5-3B | 3B | PPO | 2×H200 | <5 hrs | <10 | **<$30** | veRL |
| R1-V | Qwen2-VL-2B | 2B VLM | GRPO | 8×A100 | 30 min | 4 | **$2.62** | TRL |

DeepSeek-R1-Zero represents the largest published RLVR run: **512 H800 GPUs for 198 hours** training the 671B MoE model with GRPO. The full DeepSeek-R1 pipeline (including V3 pre-training) consumed **2.788 million H800 GPU-hours** at an estimated **$5.58M**. At the other extreme, R1-V demonstrated that RLVR can deliver meaningful gains (2B model outperforming 72B on out-of-distribution visual reasoning) in just **30 minutes on 8 A100s for $2.62**. DeepScaleR's iterative context-length scaling approach (8K→16K→24K) reduced estimated compute from ~70K to just 3,800 A100-hours — demonstrating that **curriculum-based context scaling is a critical cost optimization** for RLVR.

---

## RLVR is faster than RLHF but far slower than SFT

**GRPO eliminates the critic model that PPO requires**, reducing memory overhead by roughly 40–50% and boosting throughput by 1.7–2.5×. Traditional PPO-based RLHF requires four large models in GPU memory simultaneously (policy, reference, reward model, critic), while GRPO needs only two (policy and reference). DAPO goes further by removing the KL penalty entirely, eliminating even the reference model.

The throughput hierarchy is clear from measured data. GRPO on a 7B model achieves **1,544 tok/GPU/s** versus PPO's **907 tok/GPU/s** on an H100 — a **1.70× improvement**. On MI300X, GRPO reaches **1,748 tok/GPU/s** versus PPO's **921 tok/GPU/s** (1.90×). Community estimates suggest GRPO reduces overall training costs to roughly **1/18th of traditional PPO-based RL methods** when accounting for memory savings that enable larger batch sizes.

However, RLVR's rule-based verification advantage (no neural reward model forward pass) is substantially offset by its long rollouts. The DC-SFT paper measured directly: SFT achieves **4.9× higher training efficiency** than GRPO on equivalent VLM tasks. Multiple sources confirm the **5–10× slowdown** of online RL versus offline SFT, driven by autoregressive rollout generation consuming 70–90% of RL training time. A single RLVR training step can take **minutes to over an hour** depending on model size and rollout length, compared to seconds for SFT. The OLMo 3 32B reasoner allocated **20 H100 nodes for inference alongside 8 for training** — inference consumed 5–14× more compute than policy updates, with learner GPUs idle 75% of the time waiting for rollout data.

---

## Framework landscape for RLVR training

Four major frameworks dominate RLVR training, each with distinct strengths. The table below reflects capabilities as of early April 2026.

| Feature | OpenRLHF v0.9.9 | veRL v0.7.1 | TRL v1.0.0 | NeMo RL |
|---------|-----------------|-------------|------------|---------|
| **GRPO** | ✅ | ✅ | ✅ | ✅ |
| **DAPO** | ✅ (via flags) | ✅ (reference impl.) | ❌ | ✅ |
| **Dr. GRPO** | ✅ | ✅ | ❌ | ❌ |
| **REINFORCE++** | ✅ (native, recommended) | ✅ | ❌ | ❌ |
| **PRIME** | ❌ | ✅ | ❌ | ❌ |
| **Max proven scale** | 70B+ dense | **671B MoE** | ~72B (with DeepSpeed) | 340B+ |
| **Inference backend** | vLLM | vLLM + SGLang | vLLM | Megatron native |
| **Training backend** | DeepSpeed ZeRO-3 | FSDP/Megatron | HF Accelerate | Megatron Core |
| **Async training** | ✅ (--async_train) | ✅ (1-step off-policy) | Experimental | ✅ |
| **FP8 end-to-end** | ❌ | ❌ | ❌ | **✅** |
| **Ease of use** | Medium | Medium-High | **Highest** | Low |

**OpenRLHF** (9K GitHub stars, EMNLP 2025) is the throughput leader for dense models up to 70B, achieving **1.22–1.68× speedup over veRL** in long-CoT RLVR settings across 1.5B–14B models with 1K–8K generation lengths. Its Ray+vLLM+DeepSpeed architecture is battle-tested by Google, ByteDance, NVIDIA, and Tencent. The team explicitly recommends REINFORCE++-baseline for RLVR tasks due to its robustness across reward patterns.

**veRL** (15K GitHub stars, EuroSys 2025) has the **broadest algorithm support** and the largest proven scale — the DAPO paper's results were produced using veRL, and it has been validated on DeepSeek-V3 671B and Qwen3-235B MoE models. Its Megatron backend enables expert parallelism essential for MoE training. ByteDance's Seed-Thinking-v1.5 (86.7% AIME 2024) was trained using veRL. Note that OpenRLHF's published speed advantage was measured against veRL v0.4.0; veRL has since released significant optimizations through v0.7.1 that may have closed this gap.

**TRL** (3M monthly downloads, v1.0.0 March 2026) prioritizes accessibility over raw throughput. Its GRPOTrainer requires minimal code and integrates natively with Hugging Face's ecosystem. It is **~3.1× slower than OpenRLHF** on GRPO benchmarks, making it best suited for prototyping and smaller-scale training. The Open-R1 and Mini-R1 reproduction projects both use TRL.

**NeMo RL** (successor to deprecated NeMo-Aligner) is NVIDIA's enterprise offering, uniquely supporting **end-to-end FP8 training** and Megatron Core's full 3D parallelism suite. It trained Nemotron 3 Nano with GRPO across multiple environments simultaneously, using up to 49K-token generation lengths.

Notable emerging frameworks include **AReaL** (Ant Group/Tsinghua), achieving **2.77× speedup** via fully asynchronous RL, and **ROLL Flash** (Alibaba), reaching **2.24× speedup** on RLVR through queue scheduling and rollout-train decoupling.

---

## Cloud GPU pricing for RLVR workloads in April 2026

RLVR training demands multi-GPU clusters with high-bandwidth interconnect (NVLink intra-node, InfiniBand inter-node). Prices below are per GPU per hour, verified from provider websites in March–April 2026.

### H100 SXM 80GB

| Provider | On-Demand | Spot/Community | Reserved | InfiniBand |
|----------|-----------|---------------|----------|------------|
| Vast.ai | ~$1.54 | ~$1.50+ | Available | Varies |
| RunPod (Community) | ~$1.99–$2.49 | — | Enterprise | NVLink |
| FluidStack | ~$2.10 | — | Custom | ✅ |
| Vultr (36-mo) | $2.30 | — | 36-mo prepaid | NVLink |
| Lambda (1-Click) | **$2.76** | — | 1–3 yr custom | **✅** |
| RunPod (Secure) | ~$2.69–$2.99 | — | Enterprise | NVLink |
| DigitalOcean (8×) | $2.99 | — | $1.99 (committed) | NVLink |
| Crusoe | $3.90 | Contact sales | Custom | ✅ |
| Lambda (Instance) | $3.99–$4.29 | — | Custom | NVLink |
| Together AI | ~$3.50–$4.00 | — | 6+ day reserve | ✅ |
| CoreWeave | **$6.16** | — | Up to 60% off | ✅ |

### H200 SXM 141GB

| Provider | On-Demand | Reserved | Notes |
|----------|-----------|----------|-------|
| Vast.ai | ~$1.50–$4.00 | Available | Marketplace, variable |
| DigitalOcean | $3.44 | Multi-month discount | NVLink HGX |
| Crusoe | **$4.29** | Custom | InfiniBand |
| Together AI | $4.99 | Reserved clusters | NVLink SXM5 |
| CoreWeave | $6.31 | Up to 60% off | InfiniBand |

### MI300X 192GB

| Provider | On-Demand | Reserved | Notes |
|----------|-----------|----------|-------|
| Vast.ai | ~$0.95–$3.12 | Available | Marketplace spot from $0.95 |
| TensorWave | **$2.25** | $1.71 (dedicated) | Bare metal, Infinity Fabric |
| Vultr | $1.85 (preempt.) | $1.85 (24-mo) | 24-month prepaid |
| DigitalOcean | **$1.99** | Multi-month | Infinity Fabric |
| Crusoe | $3.45 | Custom | Infinity Fabric |

### A100 80GB SXM

| Provider | On-Demand | Spot | Notes |
|----------|-----------|------|-------|
| Vast.ai | ~$0.50–$2.00 | From ~$0.50 | Marketplace |
| RunPod (Community) | ~$0.89 | — | Per-second billing |
| Crusoe | $1.95 | $1.30 | Clean energy |
| RunPod (Secure) | ~$1.89 | — | SOC2 |
| CoreWeave | $2.70 | — | InfiniBand |
| Lambda | $2.79 | — | 8× nodes |

For serious RLVR training at scale (multi-node with InfiniBand), Lambda 1-Click Clusters at **$2.76/GPU/hr** for H100 and DigitalOcean at **$1.99/GPU/hr** for MI300X represent the strongest price-performance combinations with production-grade interconnect. Vast.ai offers the lowest absolute prices but lacks guaranteed InfiniBand connectivity.

---

## Cost per million tokens processed during RLVR training

The following calculations combine measured GRPO throughput at 7B scale (1K response length) with current GPU pricing. **These represent best-case costs** — real-world RLVR with longer rollouts will have higher per-step costs (though similar per-token costs if memory permits maintaining batch size).

### H100 SXM — 7B GRPO (1,544 tok/GPU/s = 5.56M tok/GPU/hr)

| Provider | $/GPU/hr | $/M Tokens | Notes |
|----------|----------|------------|-------|
| Vast.ai | $1.54 | **$0.28** | Marketplace; reliability varies |
| RunPod (Community) | $1.99 | $0.36 | Per-second billing |
| Lambda (1-Click) | $2.76 | $0.50 | InfiniBand clusters |
| DigitalOcean (8×) | $2.99 | $0.54 | NVLink HGX |
| Crusoe | $3.90 | $0.70 | Clean energy |
| Lambda (Instance) | $3.99 | $0.72 | Self-serve |
| CoreWeave | $6.16 | **$1.11** | Enterprise; reserved ~$2.46→$0.44 |

### MI300X — 7B GRPO (1,748 tok/GPU/s = 6.29M tok/GPU/hr)

| Provider | $/GPU/hr | $/M Tokens | Notes |
|----------|----------|------------|-------|
| Vast.ai (spot) | $0.95 | **$0.15** | Marketplace; lowest possible |
| Vultr (24-mo) | $1.85 | $0.29 | Prepaid commitment |
| DigitalOcean | $1.99 | **$0.32** | Best reliable value |
| TensorWave | $2.25 | $0.36 | Bare metal, dedicated |
| Crusoe | $3.45 | $0.55 | InfiniBand |

### Estimated cost scaling by model size (H100, best reliable pricing ~$2.76/hr)

| Model Size | Est. tok/GPU/s | M tok/GPU/hr | $/M Tokens | Est. Cost for 1B Token Run |
|-----------|---------------|--------------|------------|---------------------------|
| 7B | 1,544 (measured) | 5.56 | **$0.50** | $500 |
| 14B | ~800 (est.) | ~2.88 | ~$0.96 | $960 |
| 32B | ~375 (est.) | ~1.35 | ~$2.04 | $2,040 |
| 70B | ~160 (est.) | ~0.58 | ~$4.76 | $4,760 |

MI300X provides a **30–45% cost advantage** over H100 for RLVR training at current market rates, combining higher throughput (+13% for 7B GRPO) with lower pricing (DigitalOcean MI300X at $1.99 vs Lambda H100 at $2.76). The primary risk is ROCm ecosystem maturity — veRL supports MI300X natively, but not all frameworks have been validated on AMD hardware.

---

## Long rollouts dominate RLVR cost structure

The defining characteristic of RLVR versus traditional RLHF is the length of generated rollouts. While RLHF typically generates 512–2048 token responses, RLVR reasoning chains routinely reach **8K–32K tokens**, with production systems like DAPO using max_response_length of **20,480 tokens** and NeMo RL's Nemotron training reaching **49K tokens**. Production RLVR workload characterization (PolyTrace) shows math reasoning tasks averaging **~9,839 output tokens** per sample.

**Rollout generation consumes 70–90% of total RLVR training time.** This means the bottleneck is autoregressive decoding — a memory-bandwidth-bound operation that cannot be trivially accelerated by adding more compute. Each GRPO step generates **G completions per prompt** (typically G=8–64; DeepSeek-R1 used G=64), multiplying the generation burden. For a concrete example from the HuggingFace "Keep the Tokens Flowing" analysis: generating 512 rollouts at 8K tokens for a 32B model on 8 H100 inference GPUs takes approximately **7 minutes for generation alone**, before any gradient computation.

The long-tail distribution of rollout lengths creates severe GPU idling. ROLL Flash found that the longest responses can exceed the median by over **20×**, meaning most GPUs finish early and wait for stragglers in synchronous systems. The OLMo 3 32B reasoner's learner GPUs spent **75% of time idle** waiting for inference data. This has spawned several optimization approaches:

- **Asynchronous training** (ROLL Flash, AReaL, PipelineRL) decouples generation from training, achieving **2.0–2.8× speedups** by overlapping these phases
- **Dynamic sampling** (DAPO) filters prompts where all responses are correct or all wrong, avoiding wasted computation on zero-gradient batches — achieving the same performance with **1/3 the training steps**
- **Overlong reward shaping** (DAPO) applies soft penalties for responses exceeding a threshold rather than hard truncation, preventing training instability
- **Token-level policy gradient loss** (DAPO, veRL) averages loss across total tokens rather than per-sample-then-per-batch, preventing gradient dilution for long sequences
- **Dr. GRPO's debiased advantage** removes variance normalization and length divisors from GRPO, eliminating bias toward shorter responses and providing unbiased policy gradients
- **Clip-Higher** (DAPO) uses asymmetric clipping (ε_low=0.2, ε_high=0.28) to preserve exploration by allowing more room for increasing low-probability tokens, combating entropy collapse
- **NAT (Not All Tokens are Needed)** performs policy optimization on only **~50% of tokens** from each rollout while computing rewards on full responses, reducing activation memory
- **FP8 precision** (JetRL) achieves 1.07–1.33× rollout speedup, but naive mixed-precision (BF16 training + FP8 rollout) fails catastrophically at context lengths beyond 8K due to numerical precision mismatches
- **Iterative context scaling** (DeepScaleR) trains at 8K→16K→24K progressively, reducing total compute by **~18×** versus training at maximum length from the start

KV cache memory scales linearly with sequence length. For a Qwen-32B model, hosting with full 131K context increases memory requirements from ~70GB to approximately **400GB**. Frameworks address this through dynamic memory management (veRL's `free_cache_engine=True` offloads KV cache after rollout generation) and PagedAttention (vLLM) for non-contiguous memory allocation. Prefix caching is particularly valuable for GRPO since all G completions per prompt share the same prompt prefix — SGLang's RadixAttention provides **3–5× cache hit improvement** in this multi-completion scenario.

---

## Data quality assessment and key caveats

Every number in this report carries a confidence level that readers should understand when making cost projections.

**Measured benchmarks (high confidence):** The AMD ROCm Blog GRPO/PPO throughput numbers (veRL v0.3, 7B models, 8 GPUs, GSM8K) are the gold standard — reproducible, well-documented, and independently verified by Yotta Labs. DeepSeek-R1-Zero's training configuration (512×H800, ~198 hours) was disclosed via Stanford FMTI and Nature supplementary materials. OpenRLHF vs TRL timing comparisons come from the peer-reviewed EMNLP 2025 paper.

**Derived with caveats (medium confidence):** Wall-clock times and GPU-hours for open-source reproductions (DeepScaleR, SimpleRL-Zoo, Dr. GRPO) come from GitHub READMEs, blog posts, and WandB logs — credible but not peer-reviewed. The 70–90% rollout time proportion is consistent across ROLL Flash, veRL, OpenRLHF, and NAT papers. The RLVR vs SFT slowdown factor (5–10×) comes from the DC-SFT paper's direct measurement (4.9×) and production reports.

**Estimated with significant uncertainty (lower confidence):** Throughput estimates for 14B, 32B, and 70B models are **extrapolations** from 7B measured data combined with vLLM inference scaling ratios. Real-world throughput depends heavily on batch size, parallelism strategy, sequence length, and framework optimizations. The 14B–70B rows in the throughput and cost tables should be treated as rough order-of-magnitude guides, not precise benchmarks. Cloud GPU pricing fluctuates; spot/marketplace rates (especially Vast.ai) can vary by **2–3×** within a single week. The OpenRLHF vs veRL framework comparison was published by the OpenRLHF team against an older veRL version (v0.4.0); veRL's subsequent optimizations through v0.7.1 may have changed this relationship.

**Unresolved gaps:** No published RLVR throughput benchmarks exist for H200 GPUs. No framework has published comparable benchmarks across all GPU types. Qwen/QwQ training compute has never been publicly disclosed. DAPO's total GPU-hours on 128×H20 were not reported. The interaction between long rollout lengths (8K–32K) and per-token throughput under GPU memory pressure lacks systematic benchmarking — current data either measures short (1K) rollouts or reports only wall-clock totals without per-token rates.

## Conclusion

RLVR training costs are dominated by a single bottleneck: **autoregressive rollout generation of long reasoning chains**. The algorithmic efficiency of GRPO over PPO (1.7–2.5× throughput advantage, ~40% memory reduction) is real but secondary to the 70–90% of wall-clock time spent generating 8K–32K token completions. The most impactful cost optimizations are therefore architectural — asynchronous training (2–2.8× speedup), dynamic sampling (3× step reduction), and iterative context scaling (18× compute reduction) — rather than hardware-level. At current market rates, MI300X at $1.99/GPU/hr with 13% higher GRPO throughput than H100 offers the best raw price-performance, though H100's broader framework support and InfiniBand availability make it the safer choice for production runs. The framework choice matters enormously: OpenRLHF's 3.1× advantage over TRL and 1.2–1.7× over veRL v0.4 on identical hardware represents a larger throughput delta than any GPU generational improvement. For organizations planning RLVR training, the decision tree is: **veRL or NeMo RL for MoE models above 200B**, **OpenRLHF for dense models up to 70B where throughput is critical**, and **TRL for rapid prototyping** — then invest heavily in the async and dynamic sampling optimizations that cut wall-clock time by 2–3× regardless of hardware choice.