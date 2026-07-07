import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

def generate_diagram_1(out_dir):
    """Diagram 1 — FL System Architecture (Section III)
    Refined with larger canvas, zero text overlaps, and professional clinical color system.
    """
    fig, ax = plt.subplots(figsize=(10, 7.5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8)
    ax.axis('off')

    # Central Aggregation Server (Top)
    server_box = patches.FancyBboxPatch((3.0, 5.2), 4.0, 1.8, boxstyle="round,pad=0.2", 
                                        fc="#EBF5FB", ec="#1B4F72", lw=2)
    ax.add_patch(server_box)
    ax.text(5.0, 6.1, "Aggregation Server\n(Global Model Coordinator)", 
            ha="center", va="center", fontsize=11, fontweight="bold", color="#1B4F72")

    # Three Client Boxes (Bottom)
    clients = [
        {"x": 0.5, "y": 0.8, "name": "Hospital Client 1\n(Local Patient Data Locked)\n[Local Model Copy]"},
        {"x": 3.75, "y": 0.8, "name": "Hospital Client 2\n(Local Patient Data Locked)\n[Local Model Copy]"},
        {"x": 7.0, "y": 0.8, "name": "Hospital Client K\n(Local Patient Data Locked)\n[Local Model Copy]"}
    ]
    
    for c in clients:
        box = patches.FancyBboxPatch((c["x"], c["y"]), 2.5, 1.8, boxstyle="round,pad=0.15", 
                                     fc="#F4F6F7", ec="#566573", lw=1.5)
        ax.add_patch(box)
        ax.text(c["x"] + 1.25, c["y"] + 0.9, c["name"], 
                ha="center", va="center", fontsize=9, color="#2C3E50", linespacing=1.3)

    # Connections (Model Weight Exchanges)
    # Arrow 1: Client 1 <-> Server
    ax.annotate("", xy=(3.2, 5.0), xytext=(1.8, 2.9),
                arrowprops=dict(arrowstyle="<->", lw=2, color="#27AE60", mutation_scale=15))
    # Arrow 2: Client 2 <-> Server
    ax.annotate("", xy=(5.0, 5.0), xytext=(5.0, 2.9),
                arrowprops=dict(arrowstyle="<->", lw=2, color="#27AE60", mutation_scale=15))
    # Arrow 3: Client K <-> Server
    ax.annotate("", xy=(6.8, 5.0), xytext=(8.2, 2.9),
                arrowprops=dict(arrowstyle="<->", lw=2, color="#27AE60", mutation_scale=15))

    # Bidirectional model weight exchange labels (placed outside arrow line paths to prevent overlap)
    ax.text(1.9, 4.2, "Model Updates", rotation=54, ha="center", va="center", fontsize=8.5, color="#27AE60", fontweight="bold")
    ax.text(5.5, 3.8, "Weights Only", rotation=90, ha="center", va="center", fontsize=8.5, color="#27AE60", fontweight="bold")
    ax.text(8.1, 4.2, "Model Updates", rotation=-54, ha="center", va="center", fontsize=8.5, color="#27AE60", fontweight="bold")

    # Crossed-out Arrow representing blocked raw data transfer (DPDP Act 2023)
    ax.annotate("", xy=(5.0, 4.9), xytext=(5.0, 3.0),
                arrowprops=dict(arrowstyle="-", lw=2, color="#C0392B", linestyle="--"))
    ax.text(5.0, 4.3, "X", color="#C0392B", fontsize=32, fontweight="bold", ha="center", va="center")
    
    # Red warning box centered and padded
    ax.text(5.0, 3.2, "RAW PATIENT DATA LOCALIZED\nTransmission Blocked under DPDP Act 2023", 
            color="#C0392B", fontsize=8, fontweight="bold", ha="center", va="center",
            bbox=dict(boxstyle="round,pad=0.3", fc="#FDEDEC", ec="#E74C3C", lw=1.5))

    # Header title with plenty of breathing room
    ax.text(5.0, 7.6, "Federated Learning Silo Architecture", ha="center", va="center", fontsize=14, fontweight="bold", color="#1B4F72")

    plt.tight_layout()
    fig.savefig(os.path.join(out_dir, "fig_architecture.png"), dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("Generated refined Diagram 1.")

def generate_diagram_2(out_dir):
    """Diagram 2 — Three-Phase Research Journey (Section I/III)
    Refined for horizontal timeline with bullet alignments and zero arrow-box intersections.
    """
    fig, ax = plt.subplots(figsize=(11, 4.5))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 4)
    ax.axis('off')

    # Phase 1 Box (Synthetic Benchmark)
    p1 = patches.FancyBboxPatch((0.4, 0.6), 3.0, 2.5, boxstyle="round,pad=0.15", 
                                 fc="#EBF5FB", ec="#2E86C1", lw=2)
    ax.add_patch(p1)
    ax.text(1.9, 2.8, "Phase 1: RetinaMNIST", ha="center", va="center", fontsize=10.5, fontweight="bold", color="#1B4F72")
    p1_details = (
        "• Controlled Synthetic Benchmark\n"
        "• 1,080 Resized Images (28x28)\n"
        "• Custom 3-Layer RetinaCNN\n"
        "• Parameter Sweep (α & μ)\n"
        "• Localized Dirichlet Skew"
    )
    ax.text(1.9, 1.5, p1_details, ha="center", va="center", fontsize=8.5, color="#2C3E50", linespacing=1.3)

    # Connection 1 -> 2 (Horizontal Arrow with offset labels)
    ax.annotate("", xy=(4.2, 1.85), xytext=(3.6, 1.85),
                arrowprops=dict(arrowstyle="->", lw=2, color="#1B4F72", mutation_scale=12))
    ax.text(3.9, 2.1, "Clinical\nValidation", ha="center", va="bottom", fontsize=8, fontweight="bold", color="#1B4F72")

    # Phase 1B Box (IDRiD Only Clinical Sweep)
    p2 = patches.FancyBboxPatch((4.4, 0.6), 3.0, 2.5, boxstyle="round,pad=0.15", 
                                 fc="#E8F8F5", ec="#27AE60", lw=2)
    ax.add_patch(p2)
    ax.text(5.9, 2.8, "Phase 1B: IDRiD Only", ha="center", va="center", fontsize=10.5, fontweight="bold", color="#196F3D")
    p2_details = (
        "• Real Clinical Fundus Scans\n"
        "• 413 High-Res Patient Images\n"
        "• EfficientNet-B0 Backbone\n"
        "• High Seed-to-Seed Variance\n"
        "• Proven Statistically Underpowered"
    )
    ax.text(5.9, 1.5, p2_details, ha="center", va="center", fontsize=8.5, color="#2C3E50", linespacing=1.3)

    # Connection 2 -> 3
    ax.annotate("", xy=(8.2, 1.85), xytext=(7.6, 1.85),
                arrowprops=dict(arrowstyle="->", lw=2, color="#196F3D", mutation_scale=12))
    ax.text(7.9, 2.1, "Scale\nResolution", ha="center", va="bottom", fontsize=8, fontweight="bold", color="#196F3D")

    # Phase 2 Box (Combined Large-scale Clinical Pipeline)
    p3 = patches.FancyBboxPatch((8.4, 0.6), 3.0, 2.5, boxstyle="round,pad=0.15", 
                                 fc="#FEF9E7", ec="#D35400", lw=2)
    ax.add_patch(p3)
    ax.text(9.9, 2.8, "Phase 2: IDRiD + APTOS", ha="center", va="center", fontsize=10.5, fontweight="bold", color="#A04000")
    p3_details = (
        "• Ingested APTOS Retinal Dataset\n"
        "• 4,075 Clinical Patient Images\n"
        "• Multi-Silo Scaling Verification\n"
        "• Power Restored (Beta Locked)\n"
        "• Reclaims Centralized Upper Bound"
    )
    ax.text(9.9, 1.5, p3_details, ha="center", va="center", fontsize=8.5, color="#2C3E50", linespacing=1.3)

    # Timeline flow line header
    ax.text(6.0, 3.6, "Three-Phase Research Roadmap Summary", ha="center", va="center", fontsize=13, fontweight="bold", color="#1B4F72")

    plt.tight_layout()
    fig.savefig(os.path.join(out_dir, "fig_research_journey.png"), dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("Generated refined Diagram 2.")

def generate_diagram_3(out_dir):
    """Diagram 3 — FedProx Proximal Term Concept (Section III)
    Refined with legends positioned outside circles, clean math markers, and distinct boundaries.
    """
    fig, ax = plt.subplots(figsize=(6.5, 6))
    ax.set_xlim(-4, 4)
    ax.set_ylim(-4, 4)
    ax.axis('off')

    # Global model coordinate (Center)
    ax.plot(0, 0, 'o', color="#1B4F72", markersize=14)
    ax.text(0.3, 0.0, r"$w^t$ (Global)", fontsize=11, ha="left", va="center", color="#1B4F72", fontweight="bold")

    # Trust region circles
    circle_prox = patches.Circle((0, 0), 1.6, fill=False, color="#27AE60", linestyle="-", lw=2)
    circle_drift = patches.Circle((0, 0), 3.2, fill=False, color="#C0392B", linestyle="--", lw=1.5)
    ax.add_patch(circle_prox)
    ax.add_patch(circle_drift)

    # Label trust regions directly near curves to prevent legend overlays
    ax.text(1.2, 1.2, "FedProx Trust Region\n(Restricted Parameter Space)", color="#27AE60", fontsize=8, fontweight="bold", ha="left")
    ax.text(2.3, 2.3, "FedAvg Drift Boundary\n(Unconstrained Search Space)", color="#C0392B", fontsize=8, fontweight="bold", ha="left")

    # Client updates (constrained vs diverged)
    # Client 1 Constrained (inside trust region)
    ax.plot(-1.1, 0.9, 'o', color="#27AE60", markersize=9)
    ax.text(-1.25, 1.0, "Client 1\n(Constrained)", fontsize=8, color="#27AE60", ha="right", va="center")
    
    # Client 1 Unconstrained/Diverged (outside)
    ax.plot(-2.5, 1.8, 'x', color="#C0392B", markersize=10, mew=2.5)
    ax.text(-2.65, 1.9, "Client 1 (Diverged\nwithout leash)", fontsize=8, color="#C0392B", ha="right", va="center")
    
    # Elastic constraint indicator line
    ax.plot([-1.1, 0], [0.9, 0], color="#D35400", linestyle=":", lw=2)
    ax.text(-0.6, 0.6, r"$\mu$ regularization", color="#D35400", fontsize=9, ha="center", rotation=-36)

    # Client 2 Constrained
    ax.plot(1.0, -1.1, 'o', color="#27AE60", markersize=9)
    ax.text(1.15, -1.0, "Client 2\n(Constrained)", fontsize=8, color="#27AE60", ha="left", va="center")
    ax.plot([1.0, 0], [-1.1, 0], color="#D35400", linestyle=":", lw=2)

    # Client 2 Diverged
    ax.plot(2.2, -2.4, 'x', color="#C0392B", markersize=10, mew=2.5)
    ax.text(2.35, -2.5, "Client 2 (Diverged\nwithout leash)", fontsize=8, color="#C0392B", ha="left", va="center")

    # Header Title
    ax.text(0, 3.8, "FedProx Proximity Regularization Concept", ha="center", va="center", fontsize=12, fontweight="bold", color="#1B4F72")

    # Custom legend off-plot
    legend_elements = [
        plt.Line2D([0], [0], marker='o', color='white', markerfacecolor='#1B4F72', markersize=10, label='Global Model ($w^t$)'),
        plt.Line2D([0], [0], marker='o', color='white', markerfacecolor='#27AE60', markersize=8, label='Constrained Client Weight'),
        plt.Line2D([0], [0], marker='x', color='white', markeredgecolor='#C0392B', markersize=8, markeredgewidth=2, label='Divergent Client Weight'),
        plt.Line2D([0], [0], color='#D35400', linestyle=':', linewidth=2, label='Elastic Penalty (Leash)')
    ]
    ax.legend(handles=legend_elements, loc="lower left", fontsize=7.5, frameon=True, facecolor="#F8F9F9")

    plt.tight_layout()
    fig.savefig(os.path.join(out_dir, "fig_prox_concept.png"), dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("Generated refined Diagram 3.")

def generate_diagram_4(out_dir):
    """Diagram 4 — Dirichlet Alpha Concept (Section III)
    High fidelity side-by-side matrices representation.
    """
    fig, axes = plt.subplots(1, 4, figsize=(11.5, 3.8))
    
    alphas = [0.05, 0.1, 0.3, 1.0]
    
    np.random.seed(42)
    
    for i, alpha in enumerate(alphas):
        ax = axes[i]
        
        # Dirichlet simulation (5 clients x 5 classes)
        data = np.zeros((5, 5))
        for c in range(5):
            props = np.random.dirichlet([alpha] * 5)
            data[:, c] = props
            
        im = ax.imshow(data, cmap="YlGnBu", aspect="auto", vmin=0, vmax=1)
        ax.set_title(f"alpha = {alpha}", fontsize=10.5, fontweight="bold", color="#1B4F72")
        ax.set_xticks(range(5))
        ax.set_xticklabels([f"C{x}" for x in range(5)], fontsize=7.5)
        ax.set_yticks(range(5))
        ax.set_yticklabels([f"Class {y}" for y in range(5)], fontsize=7.5)
        
        ax.set_xlabel("Hospital Clients", fontsize=8.5)
        if i == 0:
            ax.set_ylabel("Disease Grade Class", fontsize=8.5)
            
    fig.suptitle("Dirichlet Partitioning Skew: Class Dispersion Heatmap", fontsize=12, fontweight="bold", color="#1B4F72", y=1.06)
    
    # Elegant colorbar placement
    fig.subplots_adjust(right=0.86)
    cbar_ax = fig.add_axes([0.89, 0.18, 0.02, 0.65])
    fig.colorbar(im, cax=cbar_ax, label="Relative Proportion")

    fig.savefig(os.path.join(out_dir, "fig_alpha_concept.png"), dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("Generated refined Diagram 4.")

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
