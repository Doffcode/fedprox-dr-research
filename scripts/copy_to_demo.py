import os
import shutil

def main():
    demo_dir = os.path.expanduser("~/Desktop/DEFENSE_DAY")
    figures_dir = os.path.join(demo_dir, "figures")
    os.makedirs(figures_dir, exist_ok=True)
    
    # 1. Copy report documents
    shutil.copy2("report_draft.pdf", os.path.join(demo_dir, "report_draft.pdf"))
    shutil.copy2("report_draft.docx", os.path.join(demo_dir, "report_draft.docx"))
    print("Copied report documents.")
    
    # 2. Copy walkthrough notebook
    shutil.copy2(
        "/home/shivansh/Desktop/Antigravity /projects/dibeatic_retinopathy/03_analysis_and_plots.ipynb",
        os.path.join(demo_dir, "research_walkthrough.ipynb")
    )
    print("Copied walkthrough notebook.")
    
    # 3. Copy figures from projects/dibetic_retinopathy2/results/
    results_dir = "/home/shivansh/Desktop/Antigravity /projects/dibetic_retinopathy2/results"
    results_files = {
        "fig1_convergence_curves.png": "retinamnist_fig1_convergence_curves.png",
        "fig2_accuracy_heatmap.png": "retinamnist_fig2_accuracy_heatmap.png",
        "fig3_fairness_comparison.png": "retinamnist_fig3_fairness_comparison.png",
        "fig4_phase_transition.png": "retinamnist_fig4_phase_transition.png",
        "fig5_client_sample_distribution.png": "retinamnist_fig5_client_sample_distribution.png",
        "class_distribution_alpha_0.05.png": "retinamnist_class_distribution_alpha_0.05.png",
        "stage1_validation_loss.png": "idrid_stage1_validation_loss.png",
        "fig_architecture.png": "system_fig_architecture.png",
        "fig_research_journey.png": "system_fig_research_journey.png",
        "fig_prox_concept.png": "system_fig_prox_concept.png",
        "fig_alpha_concept.png": "system_fig_alpha_concept.png"
    }
    for src, dst in results_files.items():
        src_path = os.path.join(results_dir, src)
        if os.path.exists(src_path):
            shutil.copy2(src_path, os.path.join(figures_dir, dst))
            print(f"Copied results figure {src} -> {dst}")
            
    # 4. Copy figures from projects/dibeatic_retinopathy/fedprox_research/plots/
    plots_dir = "/home/shivansh/Desktop/Antigravity /projects/dibeatic_retinopathy/fedprox_research/plots"
    plots_files = {
        "class_distribution_alpha_0.3.png": "retinamnist_class_distribution_alpha_0.3.png",
        "class_distribution_alpha_1.0.png": "retinamnist_class_distribution_alpha_1.0.png",
        "sample_progression_grid.png": "retinamnist_sample_progression_grid.png"
    }
    for src, dst in plots_files.items():
        src_path = os.path.join(plots_dir, src)
        if os.path.exists(src_path):
            shutil.copy2(src_path, os.path.join(figures_dir, dst))
            print(f"Copied plots figure {src} -> {dst}")

if __name__ == "__main__":
    main()
