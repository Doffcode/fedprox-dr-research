import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

def generate_diagram_1(out_dir):
    """Diagram 1 — FL System Architecture (Section III)"""
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8)
    ax.axis('off')

    # Aggregation Server Box
    server_box = patches.FancyBboxPatch((3.5, 5.5), 3.0, 1.8, boxstyle="round,pad=0.2", 
                                        fc="#e6f2ff", ec="#003366", lw=2)
    ax.add_patch(server_box)
    ax.text(5.0, 6.4, "Aggregation Server\n(Global Model Coordinator)", 
            ha="center", va="center", fontsize=11, fontweight="bold", color="#003366")

    # Client boxes
    clients = [
        {"x": 0.5, "y": 0.8, "name": "Hospital Client 1"},
        {"x": 3.75, "y": 0.8, "name": "Hospital Client 2"},
        {"x": 7.0, "y": 0.8, "name": "Hospital Client K"}
    ]
    
    for c in clients:
        box = patches.FancyBboxPatch((c["x"], c["y"]), 2.5, 1.8, boxstyle="round,pad=0.15", 
                                     fc="#f2f2f2", ec="#555555", lw=1.5)
        ax.add_patch(box)
        ax.text(c["x"] + 1.25, c["y"] + 0.9, f"{c['name']}\nLocal Data Locked\n& Local Model", 
                ha="center", va="center", fontsize=9, color="#333333")

    # Connect clients to server (model weights transfer)
    # Arrow 1: Client 1 to Server
    ax.annotate("", xy=(4.0, 5.3), xytext=(2.0, 2.9),
                arrowprops=dict(arrowstyle="<->", lw=2, color="#008000", mutation_scale=15))
    # Arrow 2: Client 2 to Server
    ax.annotate("", xy=(5.0, 5.3), xytext=(5.0, 2.9),
                arrowprops=dict(arrowstyle="<->", lw=2, color="#008000", mutation_scale=15))
    # Arrow 3: Client K to Server
    ax.annotate("", xy=(6.0, 5.3), xytext=(8.0, 2.9),
                arrowprops=dict(arrowstyle="<->", lw=2, color="#008000", mutation_scale=15))

    # Weight Labels
    ax.text(2.3, 4.2, "Model Weights", rotation=50, ha="center", va="center", fontsize=8, color="#008000", fontweight="bold")
    ax.text(5.5, 4.2, "Weights Only", rotation=90, ha="center", va="center", fontsize=8, color="#008000", fontweight="bold")
    ax.text(7.7, 4.2, "Model Weights", rotation=-50, ha="center", va="center", fontsize=8, color="#008000", fontweight="bold")

    # Crossed-out Arrow (Blocked Data Transmission under DPDP Act 2023)
    ax.annotate("", xy=(5.0, 5.1), xytext=(5.0, 3.2),
                arrowprops=dict(arrowstyle="->", lw=1.5, color="#cc0000", linestyle="dashed", mutation_scale=15))
    
    # Crossed out X
    ax.text(5.0, 3.8, "X", color="#cc0000", fontsize=24, fontweight="bold", ha="center", va="center")
    ax.text(5.0, 3.4, "Raw Patient Data Blocked\n(DPDP Act 2023 Compliance)", 
            color="#cc0000", fontsize=8, fontweight="bold", ha="center", va="center",
            bbox=dict(boxstyle="round,pad=0.2", fc="#ffe6e6", ec="#cc0000", lw=1))

    # Title
    ax.text(5.0, 7.8, "Federated Learning System Architecture", ha="center", va="center", fontsize=13, fontweight="bold")

    plt.tight_layout()
    fig.savefig(os.path.join(out_dir, "fig_architecture.png"), dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("Generated Diagram 1.")

def generate_diagram_2(out_dir):
    """Diagram 2 — Three-Phase Research Journey (Section I/III)"""
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 4)
    ax.axis('off')

    # Phase 1 Box
    p1 = patches.FancyBboxPatch((0.5, 0.8), 3.0, 2.4, boxstyle="round,pad=0.15", 
                                 fc="#e6f2ff", ec="#003366", lw=2)
    ax.add_patch(p1)
    ax.text(2.0, 2.8, "Phase 1: RetinaMNIST", ha="center", va="center", fontsize=10, fontweight="bold", color="#003366")
    ax.text(2.0, 1.8, "- Controlled synthetic sweep\n- 1,080 benchmark samples\n- Custom 3-layer CNN\n- Maps non-IID boundaries", 
            ha="center", va="center", fontsize=8.5, color="#333333")

    # Arrow 1 to 2
    ax.annotate("Clinical\nValidation", xy=(4.3, 2.0), xytext=(3.7, 2.0),
                arrowprops=dict(arrowstyle="->", lw=2, color="#003366", mutation_scale=12),
                ha="center", va="bottom", fontsize=8, color="#003366")

    # Phase 1B Box
    p2 = patches.FancyBboxPatch((4.5, 0.8), 3.0, 2.4, boxstyle="round,pad=0.15", 
                                 fc="#eafaf1", ec="#27ae60", lw=2)
    ax.add_patch(p2)
    ax.text(6.0, 2.8, "Phase 1B: IDRiD Only", ha="center", va="center", fontsize=10, fontweight="bold", color="#27ae60")
    ax.text(6.0, 1.8, "- Real Indian clinical data\n- 413 high-res fundus images\n- Pre-trained EfficientNet-B0\n- High seed-to-seed variance", 
            ha="center", va="center", fontsize=8.5, color="#333333")

    # Arrow 2 to 3
    ax.annotate("Underpowering\nAnalysis", xy=(8.3, 2.0), xytext=(7.7, 2.0),
                arrowprops=dict(arrowstyle="->", lw=2, color="#27ae60", mutation_scale=12),
                ha="center", va="bottom", fontsize=8, color="#27ae60")

    # Phase 2 Box
    p3 = patches.FancyBboxPatch((8.5, 0.8), 3.0, 2.4, boxstyle="round,pad=0.15", 
                                 fc="#fff9e6", ec="#d35400", lw=2)
    ax.add_patch(p3)
    ax.text(10.0, 2.8, "Phase 2: IDRiD + APTOS", ha="center", va="center", fontsize=10, fontweight="bold", color="#d35400")
    ax.text(10.0, 1.8, "- Combined scaled pipeline\n- 4,075 clinical images\n- Restores baseline accuracy\n- Statistically powered", 
            ha="center", va="center", fontsize=8.5, color="#333333")

    # Timeline flow line
    ax.text(6.0, 3.6, "Three-Phase Research Roadmap Summary", ha="center", va="center", fontsize=12, fontweight="bold")

    plt.tight_layout()
    fig.savefig(os.path.join(out_dir, "fig_research_journey.png"), dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("Generated Diagram 2.")

def generate_diagram_3(out_dir):
    """Diagram 3 — FedProx Proximal Term Concept (Section III)"""
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.set_xlim(-4, 4)
    ax.set_ylim(-4, 4)
    ax.axis('off')

    # Draw Global model at center
    ax.plot(0, 0, 'o', color="#003366", markersize=14, label="Global Model w^t")
    ax.text(0, 0.3, r"$w^t$", fontsize=12, ha="center", va="bottom", color="#003366", fontweight="bold")

    # Draw circles representing constraints
    circle_prox = patches.Circle((0, 0), 1.5, fill=False, color="#27ae60", linestyle="solid", lw=2, label="With Regularization (Leashed)")
    circle_drift = patches.Circle((0, 0), 3.0, fill=False, color="#cc0000", linestyle="dashed", lw=1.5, label="Without Regularization (Unleashed)")
    ax.add_patch(circle_prox)
    ax.add_patch(circle_drift)

    # Client updates (drifted vs prox)
    # Client 1: drifted far away
    ax.plot(-2.5, 1.5, 'x', color="#cc0000", markersize=10, mew=2)
    ax.text(-2.6, 1.6, "Client 1 (Diverged)", fontsize=8, color="#cc0000", ha="right")
    
    # Client 2: constrained by prox
    ax.plot(-1.1, 0.7, 'o', color="#27ae60", markersize=8)
    ax.text(-1.2, 0.8, "Client 1 (Constrained)", fontsize=8, color="#27ae60", ha="right")
    
    # Spring leash between global and Client 1 constrained
    ax.plot([-1.1, 0], [0.7, 0], color="#d35400", linestyle="dotted", lw=2)
    ax.text(-0.55, 0.45, r"$\mu$ penalty", color="#d35400", fontsize=9, ha="center", rotation=-32)

    # Client 3: constrained by prox
    ax.plot(0.9, -1.0, 'o', color="#27ae60", markersize=8)
    ax.text(1.0, -1.1, "Client 2 (Constrained)", fontsize=8, color="#27ae60", ha="left")
    ax.plot([0.9, 0], [-1.0, 0], color="#d35400", linestyle="dotted", lw=2)

    # Client 3 drifted
    ax.plot(2.0, -2.2, 'x', color="#cc0000", markersize=10, mew=2)
    ax.text(2.1, -2.3, "Client 2 (Diverged)", fontsize=8, color="#cc0000", ha="left")

    ax.legend(loc="upper right", fontsize=8)
    ax.text(0, 3.6, "FedProx Constraint Concept (Trust Region Constraint)", ha="center", va="center", fontsize=11, fontweight="bold")

    plt.tight_layout()
    fig.savefig(os.path.join(out_dir, "fig_prox_concept.png"), dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("Generated Diagram 3.")

def generate_diagram_4(out_dir):
    """Diagram 4 — Dirichlet Alpha Concept (Section III)"""
    fig, axes = plt.subplots(1, 4, figsize=(10, 3))
    
    alphas = [0.05, 0.1, 0.3, 1.0]
    
    # Seed generator for visual representations
    np.random.seed(42)
    
    for i, alpha in enumerate(alphas):
        ax = axes[i]
        
        # Simulate Dirichlet distribution class frequencies (5 clients x 5 classes)
        data = np.zeros((5, 5))
        for c in range(5):
            props = np.random.dirichlet([alpha] * 5)
            data[:, c] = props
            
        im = ax.imshow(data, cmap="YlGnBu", aspect="auto", vmin=0, vmax=1)
        ax.set_title(f"alpha = {alpha}", fontsize=10, fontweight="bold")
        ax.set_xticks(range(5))
        ax.set_xticklabels([f"C{x}" for x in range(5)], fontsize=7)
        ax.set_yticks(range(5))
        ax.set_yticklabels([f"L{y}" for y in range(5)], fontsize=7)
        
        if i == 0:
            ax.set_ylabel("Disease Grade Class", fontsize=8)
            ax.set_xlabel("Hospital Clients", fontsize=8)
        else:
            ax.set_xlabel("Hospital Clients", fontsize=8)
            
    fig.suptitle("Dirichlet Partitioning Skew: Class Dispersion Heatmap", fontsize=11, fontweight="bold", y=1.05)
    
    # Colorbar
    fig.subplots_adjust(right=0.85)
    cbar_ax = fig.add_axes([0.88, 0.15, 0.02, 0.7])
    fig.colorbar(im, cax=cbar_ax, label="Relative Proportion")

    fig.savefig(os.path.join(out_dir, "fig_alpha_concept.png"), dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("Generated Diagram 4.")

if __name__ == "__main__":
    out = "/home/shivansh/Desktop/Antigravity /projects/dibetic_retinopathy2/results"
    figures_dir = "/home/shivansh/Desktop/Antigravity /projects/dibetic_retinopathy2/figures"
    os.makedirs(figures_dir, exist_ok=True)
    os.makedirs(out, exist_ok=True)
    
    generate_diagram_1(figures_dir)
    generate_diagram_2(figures_dir)
    generate_diagram_3(figures_dir)
    generate_diagram_4(figures_dir)
    
    # Copy to results for document compilation
    import shutil
    shutil.copy2(os.path.join(figures_dir, "fig_architecture.png"), os.path.join(out, "fig_architecture.png"))
    shutil.copy2(os.path.join(figures_dir, "fig_research_journey.png"), os.path.join(out, "fig_research_journey.png"))
    shutil.copy2(os.path.join(figures_dir, "fig_prox_concept.png"), os.path.join(out, "fig_prox_concept.png"))
    shutil.copy2(os.path.join(figures_dir, "fig_alpha_concept.png"), os.path.join(out, "fig_alpha_concept.png"))
