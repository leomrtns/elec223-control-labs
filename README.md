# ELEC223 Interactive Control Labs

Two Streamlit applications for exploring a configurable third-order SISO system:

- `root_locus_app.py` — interactive root locus, selected closed-loop poles, stability and damping metrics.
- `bode_app.py` — interactive Bode magnitude/phase, gain and phase margins, and an optional closed-loop overlay.

Both apps use

\[
G_0(s)=\frac{s+z}{s(s+p_1)(s+p_2)}, \qquad L(s)=K G_0(s).
\]

## Create the Conda environment

```bash
conda env create -f environment.yml
conda activate elec223-control-labs
```

If the environment already exists, update it with:

```bash
conda env update -f environment.yml --prune
```

## Run the applications

In separate terminals, run:

```bash
streamlit run root_locus_app.py
```

```bash
streamlit run bode_app.py
```

Streamlit prints the local address for each application. If both run simultaneously, it automatically assigns the second app another port.

## Run the numerical checks

```bash
pytest
```

## Teaching notes

- Changing only `K` moves the selected closed-loop poles along a fixed root locus.
- Changing `p1`, `p2`, or `z` changes the open-loop model and regenerates the locus.
- A tenfold increase in `K` shifts open-loop Bode magnitude by 20 dB and leaves phase unchanged.
- Stability margins belong to the open-loop response, even when the closed-loop response is overlaid.
