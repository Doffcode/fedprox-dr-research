import os
import urllib.request
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

def render_kroki_post(text, diagram_type, output_path):
    """Post diagram markup to Kroki public API to render as PNG."""
    url = f"https://kroki.io/{diagram_type}/png"
    print(f"Rendering {diagram_type} diagram via Kroki POST to {url} ...")
    req = urllib.request.Request(
        url, 
        data=text.encode('utf-8'), 
        headers={'Content-Type': 'text/plain', 'User-Agent': 'Mozilla/5.0'}
    )
    try:
        with urllib.request.urlopen(req) as response:
            with open(output_path, 'wb') as f:
                f.write(response.read())
        print(f"SUCCESS: Rendered {diagram_type} diagram to {output_path}")
    except Exception as e:
        print(f"ERROR rendering {diagram_type} diagram: {e}")

def generate_diagram_1(out_dir):
    """Diagram 1 — FL System Architecture (Section III) using Mermaid via Kroki"""
    mermaid_code = """
    flowchart TB
      subgraph Server [Aggregation Server Coordinator]
          GlobalCoordinator["Global Model Coordinator<br>(EfficientNet-B0 / RetinaCNN)"]
      end

      subgraph Hospital1 [Hospital Client 1]
          H1Data[(Local Patient Data<br>Locked & Private)]
          H1Model[Local Model Copy]
      end

      subgraph Hospital2 [Hospital Client 2]
          H2Data[(Local Patient Data<br>Locked & Private)]
          H2Model[Local Model Copy]
      end

      subgraph HospitalK [Hospital Client K]
          HKData[(Local Patient Data<br>Locked & Private)]
          HKModel[Local Model Copy]
      end

      H1Model <--> |"Weights Only (No Raw Data)"| GlobalCoordinator
      H2Model <--> |"Weights Only (No Raw Data)"| GlobalCoordinator
      HKModel <--> |"Weights Only (No Raw Data)"| GlobalCoordinator

      H1Data -.-x |"Transmission Blocked<br>(DPDP Act 2023)"| GlobalCoordinator
      H2Data -.-x |"Transmission Blocked<br>(DPDP Act 2023)"| GlobalCoordinator
      HKData -.-x |"Transmission Blocked<br>(DPDP Act 2023)"| GlobalCoordinator

      classDef serverStyle fill:#EBF5FB,stroke:#1B4F72,stroke-width:2px,color:#1B4F72,font-weight:bold;
      classDef clientStyle fill:#F4F6F7,stroke:#566573,stroke-width:1.5px,color:#2C3E50;
      classDef blockedStyle stroke:#E74C3C,stroke-width:2px,stroke-dasharray: 5 5;
      
      class GlobalCoordinator serverStyle;
      class H1Model,H2Model,HKModel clientStyle;
    """
    render_kroki_post(mermaid_code, "mermaid", os.path.join(out_dir, "fig_architecture.png"))

def generate_diagram_2(out_dir):
    """Diagram 2 — Three-Phase Research Journey (Section I/III) using Mermaid via Kroki"""
    mermaid_code = """
    graph LR
        P1["Phase 1: RetinaMNIST<br>• Controlled Synthetic Benchmark<br>• 1,080 Resized Images (28x28)<br>• Custom 3-Layer RetinaCNN<br>• Parameter Sweep (alpha & mu)<br>• Localized Dirichlet Skew"]
        P2["Phase 1B: IDRiD Only<br>• Real Clinical Fundus Scans<br>• 413 High-Res Patient Images<br>• EfficientNet-B0 Backbone<br>• High Seed-to-Seed Variance<br>• Proven Statistically Underpowered"]
        P3["Phase 2: IDRiD + APTOS<br>• Combined Large-scale Clinical Pipeline<br>• 4,075 Clinical Patient Images<br>• Multi-Silo Scaling Verification<br>• Power Restored (Beta Locked)<br>• Reclaims Centralized Upper Bound"]

        P1 --> |Clinical Validation| P2
        P2 --> |Scale Resolution| P3

        classDef boxStyle fill:#EBF5FB,stroke:#2E86C1,stroke-width:2px,color:#1B4F72,font-weight:bold;
        classDef boxStyle2 fill:#E8F8F5,stroke:#27AE60,stroke-width:2px,color:#196F3D,font-weight:bold;
        classDef boxStyle3 fill:#FEF9E7,stroke:#D35400,stroke-width:2px,color:#A04000,font-weight:bold;
        
        class P1 boxStyle;
        class P2 boxStyle2;
        class P3 boxStyle3;
    """
    render_kroki_post(mermaid_code, "mermaid", os.path.join(out_dir, "fig_research_journey.png"))

def generate_diagram_3(out_dir):
    """Diagram 3 — FedProx Proximal Term Concept (Section III)
    High resolution conceptual math plot using Matplotlib (300 DPI).
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
