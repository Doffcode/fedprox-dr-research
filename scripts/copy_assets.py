import os
import shutil

def main():
    src_plots_dir = "/home/shivansh/Desktop/Antigravity /projects/dibeatic_retinopathy/fedprox_research/plots"
    src_results_dir = "/home/shivansh/Desktop/Antigravity /projects/dibeatic_retinopathy/fedprox_research/results"
    
    dest_results_dir = "/home/shivansh/Desktop/Antigravity /projects/dibetic_retinopathy2/results"
    dest_retina_mnist_dir = os.path.join(dest_results_dir, "retina_mnist")
    
    # Create destinations if they don't exist
    os.makedirs(dest_results_dir, exist_ok=True)
    os.makedirs(dest_retina_mnist_dir, exist_ok=True)
    
    # Figures to copy
    figures = [
        "fig1_convergence_curves.png",
        "fig2_accuracy_heatmap.png",
        "fig3_fairness_comparison.png",
        "fig4_phase_transition.png",
        "fig5_client_sample_distribution.png",
        "class_distribution_alpha_0.05.png"
    ]
    
    print("Copying figures...")
    for fig in figures:
        src_path = os.path.join(src_plots_dir, fig)
        dest_path = os.path.join(dest_results_dir, fig)
        if os.path.exists(src_path):
            shutil.copy2(src_path, dest_path)
            print(f"Copied {fig} to results/")
        else:
            print(f"WARNING: Source figure not found: {src_path}")
            
    # Copy RetinaMNIST experiment summary
    src_csv = os.path.join(src_results_dir, "experiment_summary.csv")
    dest_csv = os.path.join(dest_retina_mnist_dir, "experiment_summary.csv")
    if os.path.exists(src_csv):
        shutil.copy2(src_csv, dest_csv)
        print("Copied RetinaMNIST experiment_summary.csv to results/retina_mnist/")
    else:
        print(f"WARNING: Source CSV not found: {src_csv}")

if __name__ == "__main__":
    main()
