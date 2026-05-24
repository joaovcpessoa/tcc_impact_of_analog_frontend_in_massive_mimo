# Análise de Impacto do Front-end Analógico em Sistemas Massive MIMO

- **Autor:** João Vítor Correia Pessoa  
- **Orientador:** Prof. D.Sc. Rafael da Silva Chaves  
- **Instituição:** Centro Federal de Educação Tecnológica Celso Suckow da Fonseca (CEFET/RJ)
- **Tipo:** Projeto Final de Graduação (TCC)  
- **Ano:** 2025

## Descrição

Este repositório contém o simulador MATLAB desenvolvido para o Trabalho de Conclusão de Curso. O objetivo é avaliar o impacto das não-linearidades do front-end analógico, especificamente dos amplificadores de potência, no desempenho de BER em sistemas Massive MIMO no downlink.

Três modelos de amplificador são analisados em comparação com o amplificador ideal (Capítulo 4):

| Acrônimo | Modelo | Seção |
|----------|--------|-------|
| IDEAL | Amplificador ideal (baseline) | - |
| CLIP | Amplificador de Corte Ideal | 4.2 |
| SS | Amplificador de Estado Sólido (SSA) | 4.3 |
| TWT | Amplificador Tubo de Onda Progressiva | 4.4 |

## Parâmetros de Simulação (Tabela 5.2)

| Parâmetro | Valor |
|-----------|-------|
| Geometria do arranjo | ULA |
| Constelação | 16-QAM |
| Número de blocos | 1000 |
| Monte-Carlo (posições dos UEs) | 10 |
| Monte-Carlo (desvanecimento em pequena escala) | 10 |
| Número de antenas M | {64, 128, 256} |
| Número de terminais K | {M/4, M/2, M} |
| SNR no downlink | −10 a 30 dB |
| Modelo de canal | Desvanecimento Rician (κ = 10 dB), ULA |
| Pré-codificadores | MF, ZF, MMSE |
| Link analisado | Downlink |

## Estrutura do Repositório

```
./src
├── matlab
│   ├── functions
│   │   ├── amplify_signal_twt.m
│   │   ├── amplify_signal.m
│   │   ├── decode_signal.m
│   │   ├── precode_signal.m
│   │   ├── normalize_precoded_signal.m
│   │   ├── normalize_decoded_signal.m
│   │   ├── rician_channel_generator.m
│   │   └── user_position_generator.m
│   ├── amplitude_analysis.m
│   ├── dl_ber.m
│   ├── load_env.m
│   ├── plot_amplitude_phase.m
│   ├── plot_ber.m
│   ├── plot_constellation.m
│   └── ul_ber.m
└── python
    ├── massive_mimo_sim/
    │   ├── __init__.py
    │   ├── qam.py
    │   ├── amplifiers.py
    │   ├── channel.py
    │   ├── precoders.py
    │   ├── simulation.py
    │   └── plotting.py
    └── run_simulation.py
```

## Como Reproduzir os Resultados

### MATLAB

#### Arquivo `.env`

Crie um arquivo `.env` dois níveis acima do diretório dos scripts com os seguintes campos:

```
CPU_SIMULATION_SAVE_PATH=
CPU_FUNCTIONS_PATH=
CPU_PLOT_BER_PATH=
```

#### Simulação de BER no downlink

Configure as variáveis no início de `ber_downlink.m` antes de executar:

```matlab
precoder_type = 'ZF';   % 'MF' | 'ZF' | 'MMSE'
% K deve estar definido no workspace (ou descomentar "K = ..." dentro do script)
K = 64;                 % M/4 para M=256
```

Execute para cada combinação de `(M, K, precoder_type)`:

```matlab
run ber_downlink.m
```

Cada execução salva um arquivo `.mat` com nome `dl_ber_<precoder>_ss_<M>_<K>.mat`.

Cenários:

| M | K | Precodificadores | Referência |
|---|---|-----------------|-----------|
| 64 | 16, 32, 64 | MF, ZF, MMSE | Figs. 5.1 (CLIP), 5.4 (SS), 5.7 (TWT) |
| 128 | 32, 64, 128 | MF, ZF, MMSE | Figs. 5.2, 5.5, 5.8 |
| 256 | 64, 128, 256 | MF, ZF, MMSE | Figs. 5.3, 5.6, 5.9 |

#### Curvas de amplitude dos amplificadores

Gera os dados das transferências AM-AM (Figuras 4.2 e 4.3 do TCC).

```matlab
run amplitude_analysis.m
run plot_amplitude_phase.m
```

#### Visualização dos resultados

```matlab
run plot_ber.m
run plot_constellation.m
```

---

### Python

```bash
pip install numpy matplotlib scipy

# Figuras de amplitude apenas (< 1 segundo)
python run_simulation.py --amp-only

# Monte Carlo reduzido (n_mc1=n_mc2=3, ~minutos por config)
python run_simulation.py --quick

# Simulação completa igual ao MATLAB (n_mc1=n_mc2=10, várias horas)
python run_simulation.py
```

Os resultados são salvos em `simulation_results/` por padrão.  
Use `--outdir <caminho>` para alterar o diretório.  
Use `--force` para forçar re-execução mesmo com cache `.npz` existente.

#### Figuras geradas

| Arquivo | Figura do TCC | Descrição |
|---------|--------------|-----------|
| `fig4_2_clip_am_am.png` | Fig 4.2 | Curva AM-AM do CLIP |
| `fig4_3_ss_am_am.png` | Fig 4.3 | Curvas AM-AM do SS (p=1,2,3; A0=1,2) |
| `fig4_4_twt_am_am_pm.png` | Fig 4.4 | Curvas AM-AM e AM-PM do TWT |
| `fig5.1_ber_clip_M64.png` | Fig 5.1 | BER vs SNR – CLIP, M=64 |
| `fig5.2_ber_clip_M128.png` | Fig 5.2 | BER vs SNR – CLIP, M=128 |
| `fig5.3_ber_clip_M256.png` | Fig 5.3 | BER vs SNR – CLIP, M=256 |
| `fig5.4_ber_ss_M64.png` | Fig 5.4 | BER vs SNR – SS, M=64 |
| `fig5.5_ber_ss_M128.png` | Fig 5.5 | BER vs SNR – SS, M=128 |
| `fig5.6_ber_ss_M256.png` | Fig 5.6 | BER vs SNR – SS, M=256 |
| `fig5.7_ber_twt_M64.png` | Fig 5.7 | BER vs SNR – TWT, M=64 |
| `fig5.8_ber_twt_M128.png` | Fig 5.8 | BER vs SNR – TWT, M=128 |
| `fig5.9_ber_twt_M256.png` | Fig 5.9 | BER vs SNR – TWT, M=256 |

#### Reprodutibilidade

- Todos os sorteios aleatórios usam `numpy.random.default_rng(seed=42)`.
- Os resultados de BER de cada par `(amplificador, M)` são cacheados em `.npz`.  
  Os gráficos podem ser regenerados a partir do cache sem re-simular.
- A simulação replica fielmente o `dl_ber.m` do MATLAB, incluindo o divisor `M`  
  (e não `N_BLK`) na normalização por antena de `normalize_precoded_signal.m`.
