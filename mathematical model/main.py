# main.py
import argparse
from simulations.run_simulation import run_simulation

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run boat formation simulation.")
    parser.add_argument("--plot", action="store_true", help="Whether to plot the formations.")

    args = parser.parse_args()

    run_simulation(with_plot=args.plot)
