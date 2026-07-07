import os
import sys
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
import pandas as pd
import subprocess

def set_cell_shading(cell, color_hex):
    """Set background color of a table cell."""
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), color_hex)
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Set internal cell margins (padding) in twentieths of a point (dxa)."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m_name, m_val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m_name}')
        node.set(qn('w:w'), str(m_val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def set_table_borders(table):
    """Apply elegant light gray borders to the table."""
    tblPr = table._tbl.tblPr
    tblBorders = OxmlElement('w:tblBorders')
    for b_name in ['top', 'left', 'bottom', 'right', 'insideH', 'insideV']:
        border = OxmlElement(f'w:{b_name}')
        border.set(qn('w:val'), 'single')
        border.set(qn('w:sz'), '4')  # 1/8 pt
        border.set(qn('w:space'), '0')
        border.set(qn('w:color'), 'CCCCCC')
        tblBorders.append(border)
    tblPr.append(tblBorders)

def clean_text(text):
    """Remove manual newlines and double spaces from multi-line text blocks
    to prevent Word from stretching them during justification.
    """
    if not text:
        return ""
    lines = [line.strip() for line in text.split('\n')]
    cleaned = " ".join(line for line in lines if line)
    while "  " in cleaned:
        cleaned = cleaned.replace("  ", " ")
    return cleaned

def add_paragraph_with_spacing(doc, text="", style='Normal', space_before=0, space_after=6, line_spacing=1.15, align=WD_ALIGN_PARAGRAPH.JUSTIFY):
    """Add paragraph with custom spacing, line height, and text cleaning."""
    cleaned_text = clean_text(text)
    p = doc.add_paragraph(cleaned_text, style=style)
    p.alignment = align
    p_format = p.paragraph_format
    p_format.space_before = Pt(space_before)
    p_format.space_after = Pt(space_after)
    p_format.line_spacing = line_spacing
    return p

def add_equation_block(doc, equation_text, label=""):
    """Add a centered mathematical equation block with Times New Roman Italic styling."""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(8)
    p.paragraph_format.keep_with_next = True
    
    run = p.add_run(equation_text)
    run.font.name = 'Times New Roman'
    run.font.size = Pt(11)
    run.font.italic = True
    
    if label:
        p.add_run(f"\t\t\t\t\t\t\t\t\t{label}")
    return p

def add_heading_with_spacing(doc, text, level, space_before=12, space_after=6):
    """Add styled heading with custom spacing."""
    h = doc.add_heading(text, level=level)
    h.paragraph_format.space_before = Pt(space_before)
    h.paragraph_format.space_after = Pt(space_after)
    h.paragraph_format.keep_with_next = True
    
    # Ensure headings use Times New Roman and Dark Blue
    for run in h.runs:
        run.font.name = 'Times New Roman'
        run.font.bold = True
        run.font.color.rgb = RGBColor(0, 51, 102)
    return h

def main():
    print("Initializing document builder...")
    doc = Document()
    
    # Page setup - Standard 1 inch margins
    for section in doc.sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)
        
    # Style configuration - Normal (Body Text)
    style_normal = doc.styles['Normal']
    font_normal = style_normal.font
    font_normal.name = 'Times New Roman'
    font_normal.size = Pt(11)
    font_normal.color.rgb = RGBColor(0, 0, 0)
    
    # Configure Heading 1
    style_h1 = doc.styles['Heading 1']
    font_h1 = style_h1.font
    font_h1.name = 'Times New Roman'
    font_h1.size = Pt(16)
    font_h1.bold = True
    font_h1.color.rgb = RGBColor(0, 51, 102)
    
    # Configure Heading 2
    style_h2 = doc.styles['Heading 2']
    font_h2 = style_h2.font
    font_h2.name = 'Times New Roman'
    font_h2.size = Pt(13)
    font_h2.bold = True
    font_h2.color.rgb = RGBColor(0, 51, 102)

    # Configure Heading 3
    style_h3 = doc.styles['Heading 3']
    font_h3 = style_h3.font
    font_h3.name = 'Times New Roman'
    font_h3.size = Pt(11.5)
    font_h3.bold = True
    font_h3.color.rgb = RGBColor(0, 51, 102)

    # --- TITLE ---
    title_p = doc.add_paragraph()
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title_p.paragraph_format.space_after = Pt(18)
    title_run = title_p.add_run("Federated Learning for Diabetic Retinopathy Detection: An Empirical Study of FedProx Under Data Heterogeneity in Indian Clinical Settings")
    title_run.font.name = 'Times New Roman'
    title_run.font.size = Pt(22)
    title_run.font.bold = True
    title_run.font.color.rgb = RGBColor(0, 51, 102)
    
    # --- AUTHOR ---
    author_p = doc.add_paragraph()
    author_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    author_p.paragraph_format.space_after = Pt(24)
    author_run = author_p.add_run("M.Tech Research Project\nDepartment of Computer Applications\nNational Institute of Technology, Tiruchirappalli, Tamil Nadu, India")
    author_run.font.name = 'Times New Roman'
    author_run.font.size = Pt(11)
    author_run.font.italic = True
    
    # --- ABSTRACT ---
    add_heading_with_spacing(doc, "Abstract", level=2, space_before=12, space_after=4)
    abstract_text = (
        "Diabetic retinopathy is one of the leading causes of preventable blindness in India, a country with over 101 million "
        "people living with diabetes. Screening is the bottleneck: most rural areas simply don't have enough ophthalmologists, "
        "and a large share of cases go undiagnosed until vision loss is already advanced. Deep learning models can grade retinal "
        "images automatically, but training them well normally means pooling large amounts of patient data from different "
        "hospitals — something India's Digital Personal Data Protection Act (2023) makes legally difficult, since it requires "
        "patient data to stay where it was collected. Federated learning offers a way around this: instead of moving data "
        "to a central server, the model itself moves between hospitals, and only its weights are shared. "
        "This project builds a federated learning simulation from scratch to study how FedAvg and FedProx behave when hospital "
        "data is highly imbalanced — some clinics seeing mostly healthy patients, others seeing mostly severe cases. We test "
        "this on two datasets: RetinaMNIST, a small controlled benchmark, and IDRiD, a real clinical dataset collected in "
        "Karnataka, India. The central finding is that FedProx doesn't behave the same way across all conditions — it can "
        "hurt accuracy when data is extremely skewed, but help once the skew is more moderate, revealing a clear switch-over "
        "point that hasn't been characterized this way before. We also find that FedProx makes the worst-performing hospital "
        "substantially more accurate, even in cases where it doesn't change the overall average — a fairness effect that "
        "matters more in a clinical setting than raw accuracy alone. Finally, a statistical power analysis suggests that "
        "IDRiD's small size limits how confidently these effects can be measured, which motivated scaling up with a "
        "combined IDRiD+APTOS dataset."
    )
    add_paragraph_with_spacing(doc, abstract_text, line_spacing=1.15, align=WD_ALIGN_PARAGRAPH.JUSTIFY)
    
    # --- KEYWORDS ---
    keywords_p = doc.add_paragraph()
    keywords_p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    keywords_p.paragraph_format.space_after = Pt(18)
    k_label = keywords_p.add_run("Keywords: ")
    k_label.bold = True
    keywords_p.add_run("Federated Learning, Diabetic Retinopathy, FedProx, Data Heterogeneity, DPDP Act, Medical Imaging, Client Fairness")
    
    # --- SECTION I: INTRODUCTION ---
    add_heading_with_spacing(doc, "Section I: Introduction", level=1, space_before=18)
    
    intro_1 = (
        "Diabetic retinopathy develops when high blood sugar damages the blood vessels in the retina. Left unchecked, it leads "
        "to permanent vision loss — but caught early, it's manageable. The problem in India isn't the disease itself, it's access: "
        "there simply aren't enough ophthalmologists to screen the country's diabetic population, and a large share of patients "
        "don't get diagnosed until the damage is already severe. Convolutional neural networks have gotten quite good at grading "
        "retinal images automatically, but they need a lot of varied training data to generalize across different cameras, "
        "lighting setups, and patient populations. That data usually lives in different hospitals, and getting it all into one "
        "place isn't just a technical problem — it runs into India's 2023 data protection law directly."
    )
    add_paragraph_with_spacing(doc, intro_1)
    
    intro_2 = (
        "The DPDP Act requires that personal data, including medical scans, largely stay where it was collected, with strict "
        "rules around consent and deletion. That leaves hospitals in an awkward spot: they can't send their data elsewhere to "
        "build a shared model, but on their own, most clinics don't have enough images (or enough variety in cases) to train "
        "something reliable. Federated learning is built for exactly this situation — the model is trained locally at each hospital "
        "and only its parameters are sent to a central server for averaging, so the raw scans never leave the building."
    )
    add_paragraph_with_spacing(doc, intro_2)
    
    intro_3 = (
        "The standard method, FedAvg, works well when different hospitals' data looks roughly similar. It doesn't work as well when "
        "it doesn't. In practice, one hospital's patient population might be mostly mild or undiagnosed cases, while another sees "
        "almost exclusively severe, referred cases — and when each hospital trains on only its own skewed slice of the world, "
        "their models start pulling in different directions. Averaging models that disagree this much doesn't produce a good "
        "global model; it produces one that's confused. FedProx was proposed as a fix, adding a term to each hospital's local "
        "training that discourages it from drifting too far from the shared model. What's less clear — and what this project "
        "investigates — is exactly when that correction actually helps, and when it gets in the way."
    )
    add_paragraph_with_spacing(doc, intro_3)
    
    # Diagram 2 - Research Journey inserted at the end of Section I
    p_img_journey = doc.add_paragraph()
    p_img_journey.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_img_journey.paragraph_format.space_before = Pt(12)
    p_img_journey.paragraph_format.space_after = Pt(4)
    p_img_journey.add_run().add_picture("results/fig_research_journey.png", width=Inches(5.8))
    p_img_journey_cap = add_paragraph_with_spacing(doc, "Figure 1: Research roadmap summary detailing the three-phase methodology transition from RetinaMNIST benchmark to IDRiD + APTOS clinical scaling.", align=WD_ALIGN_PARAGRAPH.CENTER)
    p_img_journey_cap.runs[0].font.italic = True
    
    # --- SECTION II: RELATED WORK ---
    add_heading_with_spacing(doc, "Section II: Related Work", level=1, space_before=18)
    
    rw_1 = (
        "Most work on collaborative learning for medical imaging falls into three buckets: standard centralized classification "
        "models, federated optimization algorithms designed to combat client drift, and empirical tests under simulated data skew."
    )
    add_paragraph_with_spacing(doc, rw_1)

    rw_2 = (
        "Centralized deep learning models for diabetic retinopathy have gotten very good, typically using backbones like ResNet and "
        "EfficientNet. The catch is that they rely on having all the training data in one place. Federated learning [1] was "
        "introduced to avoid this requirement in healthcare. Recent papers [7] show it is possible to train diagnostic classifiers "
        "on retinal images without moving raw scans. Even so, medical federated learning still struggles with clinical skew and "
        "variation in camera hardware, which can cause local updates to diverge."
    )
    add_paragraph_with_spacing(doc, rw_2)

    rw_3 = (
        "To keep local training from drifting, researchers usually modify the local loss function. The base method, FedAvg [1], "
        "simply averages client weights. FedProx [2] restricts how far local parameters can wander by adding an L₂ proximal penalty "
        "that keeps client updates anchored near the global model. Meanwhile, SCAFFOLD [3] uses control variates to track and "
        "correct gradient updates. Surveys [5] suggest that while regularization can stabilize training under moderate skew, it "
        "often hurts convergence under extreme non-IID conditions. The threshold where this behavior flips is what we focus on."
    )
    add_paragraph_with_spacing(doc, rw_3)

    rw_4 = (
        "Simulating clinical heterogeneity in a lab setting is typically done using Dirichlet distributions. Class-wise Dirichlet "
        "sampling, introduced by Hsu et al. [4], distributes classes to clients based on a concentration parameter α. Lower α "
        "values (like α < 0.1) simulate severe skew, where some clinics lack entire categories of disease. Lightweight benchmarks "
        "like RetinaMNIST (part of MedMNIST v2) [6] let us run wide hyperparameter sweeps on small images, isolating the effect "
        "of skew and regularization without the computational baggage of high-resolution processing."
    )
    add_paragraph_with_spacing(doc, rw_4)

    # --- SECTION III: METHODOLOGY ---
    add_heading_with_spacing(doc, "Section III: Methodology", level=1, space_before=18)
    
    add_heading_with_spacing(doc, "1. Network Architectures", level=2)
    meth_arch_1 = (
        "For the small 28x28 images in RetinaMNIST, we use RetinaCNN, a basic 3-layer convolutional network. It consists of "
        "three convolutional blocks: the first has 16 filters (3×3 kernel, stride 1, padding 1) with BatchNorm and MaxPool, "
        "shrinking the map to 14x14; the second has 32 filters (yielding 7x7); and the third has 64 filters (yielding 3x3). "
        "The classifier flattens this 576-dimensional output and runs it through a 128-unit linear layer, ReLU, dropout (p=0.3), "
        "and a final 5-unit projection. This model contains exactly 98,309 parameters, which is small enough to train quickly "
        "without overfitting on small partitions."
    )
    add_paragraph_with_spacing(doc, meth_arch_1)
    
    meth_arch_2 = (
        "For the clinical IDRiD images, we use a pre-trained EfficientNet-B0 backbone (about 5.3 million parameters) via the "
        "timm library. We swap the final classification head for a 5-unit linear layer to match the diabetic retinopathy grades. "
        "The fundus photographs are resized to 224x224, normalized, and augmented with random crops, flips, rotation, and color "
        "jitter to mimic variations in camera hardware and lighting."
    )
    add_paragraph_with_spacing(doc, meth_arch_2)
    
    add_heading_with_spacing(doc, "2. Statistical Data Heterogeneity Modeling", level=2)
    meth_het_1 = (
        "We simulate skewed data distributions across K hospital clients using Dirichlet partitioning [4]. For each disease grade "
        "c ∈ {0, 1, 2, 3, 4}, we draw client proportions from a Dirichlet distribution with parameter α. Small α values "
        "(e.g., α = 0.05) mean some classes are completely missing from certain clients. We sweep α through 0.05, 0.1, 0.3, "
        "and 1.0 to see how optimization algorithms handle the transition from extreme class skew to a near-IID setup."
    )
    add_paragraph_with_spacing(doc, meth_het_1)
    
    # Diagram 4 - Dirichlet Alpha Concept Heatmap inserted near partitioning text
    p_img_alpha = doc.add_paragraph()
    p_img_alpha.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_img_alpha.paragraph_format.space_before = Pt(12)
    p_img_alpha.paragraph_format.space_after = Pt(4)
    p_img_alpha.add_run().add_picture("results/fig_alpha_concept.png", width=Inches(5.0))
    p_img_alpha_cap = add_paragraph_with_spacing(doc, "Figure 2: Dirichlet concentration parameter concept illustrating the progression from extreme class sparsity (alpha = 0.05) to a uniform clinical distribution (alpha = 1.0).", align=WD_ALIGN_PARAGRAPH.CENTER)
    p_img_alpha_cap.runs[0].font.italic = True
    
    add_heading_with_spacing(doc, "3. Federated Simulation Environment", level=2)
    meth_env_1 = (
        "We built the federated loop in a single process rather than using distributed frameworks like Flower or Ray. This avoids "
        "the VRAM overhead and configuration headaches that usually come with running distributed software on a single workstation. "
        "All training runs on a local Ubuntu workstation with an Intel i7-13700 CPU and a single NVIDIA RTX A2000 GPU (12GB VRAM). "
        "The simulation handles PyTorch CUDA allocation, using four workers and pinned memory to prevent data-loading bottlenecks. "
        "Figure 3 shows this setup, highlighting the boundary that keeps patient data inside each client silo."
    )
    add_paragraph_with_spacing(doc, meth_env_1)
    
    # Diagram 1 - FL System Architecture inserted in Simulation section
    p_img_arch = doc.add_paragraph()
    p_img_arch.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_img_arch.paragraph_format.space_before = Pt(12)
    p_img_arch.paragraph_format.space_after = Pt(4)
    p_img_arch.add_run().add_picture("results/fig_architecture.png", width=Inches(4.5))
    p_img_arch_cap = add_paragraph_with_spacing(doc, "Figure 3: System architecture of the manual federated loop, demonstrating patient data localization compliance under the Indian DPDP Act 2023.", align=WD_ALIGN_PARAGRAPH.CENTER)
    p_img_arch_cap.runs[0].font.italic = True
    
    add_heading_with_spacing(doc, "4. Optimization Algorithms and Formulations", level=2)
    meth_alg_1 = (
        "In Federated Averaging (FedAvg), the server updates the global model by taking a sample-weighted average of the client "
        "parameters at each round:"
    )
    add_paragraph_with_spacing(doc, meth_alg_1, space_after=2)
    add_equation_block(doc, "wᵗ⁺¹ = ∑_{k=1}^K (n_k / N) · w_k^(t+1)")
    
    meth_alg_1b = (
        "where w_k^(t+1) represents the local weights updated at client k over E epochs using standard Cross-Entropy Loss."
    )
    add_paragraph_with_spacing(doc, meth_alg_1b, space_before=2)
    
    meth_alg_2 = (
        "FedProx [2] adds a proximal penalty to the local client loss to penalize updates that move too far from the global starting point:"
    )
    add_paragraph_with_spacing(doc, meth_alg_2, space_after=2)
    add_equation_block(doc, "L_k(w; wᵗ) = F_k(w) + (μ / 2) · ‖w - wᵗ‖₂²")
    
    meth_alg_2b = (
        "The parameter μ scales this penalty, which acts as a trust region constraint around the global model wᵗ."
    )
    add_paragraph_with_spacing(doc, meth_alg_2b, space_before=2)
    
    # Diagram 3 - FedProx concept inserted immediately after FedProx equation
    p_img_prox = doc.add_paragraph()
    p_img_prox.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_img_prox.paragraph_format.space_before = Pt(12)
    p_img_prox.paragraph_format.space_after = Pt(4)
    p_img_prox.add_run().add_picture("results/fig_prox_concept.png", width=Inches(4.2))
    p_img_prox_cap = add_paragraph_with_spacing(doc, "Figure 4: Concept diagram of the FedProx regularizer, demonstrating the elastic leash mechanism limiting weight updates to a trust region close to global coordinates.", align=WD_ALIGN_PARAGRAPH.CENTER)
    p_img_prox_cap.runs[0].font.italic = True
    
    meth_alg_3 = (
        "SCAFFOLD [3] takes a different approach, adjusting the local gradient step using client and server control variates (c_k and c):"
    )
    add_paragraph_with_spacing(doc, meth_alg_3, space_after=2)
    add_equation_block(doc, "g_k(w) = ∇F_k(w) + (c - c_k)")
    
    meth_alg_3b = (
        "We implement the gradient-accumulation (Option II) version of SCAFFOLD. This avoids issues when using SGD with momentum "
        "or adaptive optimizers by updating the client control variates from the uncorrected gradients accumulated during the step:"
    )
    add_paragraph_with_spacing(doc, meth_alg_3b, space_before=2, space_after=2)
    add_equation_block(doc, "c_k⁺ ← (1 / K_steps) · ∑_{s=1}^{K_steps} g_raw(y_s)")
    
    meth_alg_3c = (
        "The server then updates the global control variate by averaging the changes:"
    )
    add_paragraph_with_spacing(doc, meth_alg_3c, space_before=2, space_after=2)
    add_equation_block(doc, "c ← c + (1 / N_clients) · ∑ (c_k⁺ - c_k)")
    
    # --- SECTION IV: RESULTS & DISCUSSION ---
    add_heading_with_spacing(doc, "Section IV: Results & Discussion", level=1, space_before=18)
    
    add_heading_with_spacing(doc, "1. Centralized Baseline & Local Optimizations", level=2)
    res_1 = (
        "To establish a baseline, we trained a model centrally on all 413 IDRiD images using AdamW (learning rate η=1e-4, "
        "weight decay 1e-2) and a Cosine Annealing scheduler (T_max=25). This centralized model peaked at 55.34% global accuracy "
        "at epoch 4 (Table 1). For comparison, a single hospital client (Client 0) training on only its local slice of the data "
        "(301 images, α=0.3) achieves a peak global accuracy of just 42.72% at round 19. The local model's confusion matrix in Table 1 "
        "shows a heavy bias: it overpredicts Class 2 because its local data is skewed, demonstrating why small clinics struggle "
        "to build useful models on their own."
    )
    add_paragraph_with_spacing(doc, res_1)
    
    # TABLE 1: Centralized Baseline vs Local Model
    table1 = doc.add_table(rows=6, cols=3)
    table1.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(table1)
    
    headers1 = ["Parameter / Metric", "Centralized Baseline Model", "Local Client Model (Client 0, alpha=0.3)"]
    for i, h_text in enumerate(headers1):
        cell = table1.cell(0, i)
        cell.text = h_text
        set_cell_shading(cell, "003366")
        set_cell_margins(cell)
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        cell.paragraphs[0].runs[0].font.bold = True
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        
    t1_data = [
        ["Backbone Architecture", "EfficientNet-B0 (Pre-trained)", "EfficientNet-B0 (Pre-trained)"],
        ["Optimizer / Learning Rate", "AdamW, lr = 1e-4", "AdamW, lr = 1e-4"],
        ["Epoch / Round locked", "Epoch 4", "Epoch 19 (Local Round 1)"],
        ["Training Samples Used", "413 fundus images (Full)", "301 fundus images (Client 0 partition)"],
        ["Peak Global Test Accuracy", "55.34%", "42.72%"]
    ]
    for row_idx, row_data in enumerate(t1_data):
        for col_idx, text in enumerate(row_data):
            cell = table1.cell(row_idx + 1, col_idx)
            cell.text = text
            set_cell_margins(cell)
            if (row_idx + 1) % 2 == 1:
                set_cell_shading(cell, "F2F2F2")
            cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.LEFT if col_idx == 0 else WD_ALIGN_PARAGRAPH.CENTER
            
    p_cap1 = add_paragraph_with_spacing(doc, "Table 1: Hyperparameter configurations and accuracy outcomes for Centralized Baseline vs. Local Client Model on IDRiD data.", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=6, space_after=12)
    p_cap1.runs[0].font.italic = True
    
    # Client 0 Confusion Matrix
    cm_p = doc.add_paragraph()
    cm_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cm_p_run = cm_p.add_run("Confusion Matrix (Client 0, alpha=0.3, best epoch 19):")
    cm_p_run.font.bold = True
    cm_p_run.font.size = Pt(10)
    
    cm_tbl = doc.add_table(rows=6, cols=6)
    cm_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(cm_tbl)
    cm_headers = ["Actual \\ Pred", "Class 0", "Class 1", "Class 2", "Class 3", "Class 4"]
    for i, h_text in enumerate(cm_headers):
        cell = cm_tbl.cell(0, i)
        cell.text = h_text
        set_cell_shading(cell, "333333")
        set_cell_margins(cell)
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        cell.paragraphs[0].runs[0].font.bold = True
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        
    cm_data = [
        ["Class 0", "6", "0", "28", "0", "0"],
        ["Class 1", "1", "0", "4", "0", "0"],
        ["Class 2", "0", "0", "32", "0", "0"],
        ["Class 3", "1", "0", "12", "2", "4"],
        ["Class 4", "0", "0", "8", "1", "4"]
    ]
    for row_idx, row_data in enumerate(cm_data):
        for col_idx, text in enumerate(row_data):
            cell = cm_tbl.cell(row_idx + 1, col_idx)
            cell.text = text
            set_cell_margins(cell)
            if (row_idx + 1) % 2 == 1:
                set_cell_shading(cell, "F9F9F9")
            cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.LEFT if col_idx == 0 else WD_ALIGN_PARAGRAPH.CENTER
            
    p_cap_cm = add_paragraph_with_spacing(doc, "Confusion Matrix of Client 0 local model evaluated on the shared global test set, indicating severe majority class bias (Class 2) and class exclusion.", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=6, space_after=12)
    p_cap_cm.runs[0].font.italic = True
    
    # Embed Stage 1 Validation Loss figure
    p_img_loss = doc.add_paragraph()
    p_img_loss.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_img_loss.paragraph_format.space_before = Pt(12)
    p_img_loss.paragraph_format.space_after = Pt(4)
    p_img_loss.add_run().add_picture("results/stage1_validation_loss.png", width=Inches(4.5))
    p_img_loss_cap = add_paragraph_with_spacing(doc, "Figure 5: Validation loss progression during localized IDRiD training, showing early baseline optimization.", align=WD_ALIGN_PARAGRAPH.CENTER)
    p_img_loss_cap.runs[0].font.italic = True
    
    add_heading_with_spacing(doc, "2. RetinaMNIST Hyperparameter Grid Sweep Results", level=2)
    res_2 = (
        "Table 2 shows the full sweep across heterogeneity levels and regularization strengths, averaged over three seeds. "
        "The pattern that emerges is not what a naive reading of FedProx would predict. Under severe skew (α = 0.05 and 0.1), "
        "pushing the regularization strength up hurts rather than helps — at α = 0.1, going from no regularization to μ = 1.0 "
        "drops accuracy from 43.50% to 41.00%. It's only once the data becomes more balanced (α = 0.3 and above) that the "
        "same strong regularization starts paying off, reaching 51.50% versus FedAvg's 46.92% — a genuine 4.58-point gain. "
        "In other words, FedProx isn't uniformly better or worse than FedAvg; its usefulness flips depending on how unevenly the "
        "data is distributed in the first place, and that crossover happens somewhere between α = 0.1 and α = 0.3."
    )
    add_paragraph_with_spacing(doc, res_2)
    
    # Read and aggregate RetinaMNIST data programmatically to guarantee correctness
    df_rm = pd.read_csv('/home/shivansh/Desktop/Antigravity /projects/dibetic_retinopathy2/results/retina_mnist/experiment_summary.csv')
    grouped_rm = df_rm.groupby(['alpha', 'strategy', 'mu'])[['final_accuracy', 'best_accuracy', 'accuracy_std']].mean().reset_index()
    grouped_rm = grouped_rm.sort_values(by=['alpha', 'strategy', 'mu']).reset_index(drop=True)
    
    # TABLE 2: RetinaMNIST Results
    table2 = doc.add_table(rows=len(grouped_rm) + 1, cols=6)
    table2.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(table2)
    
    headers2 = ["Alpha (Heterogeneity)", "Strategy", "Mu (Penalty)", "Mean Final Accuracy", "Mean Best Accuracy", "Client-to-Client Std"]
    for i, h_text in enumerate(headers2):
        cell = table2.cell(0, i)
        cell.text = h_text
        set_cell_shading(cell, "003366")
        set_cell_margins(cell)
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        cell.paragraphs[0].runs[0].font.bold = True
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        
    for row_idx, row in grouped_rm.iterrows():
        alpha_val = row['alpha']
        strat_val = row['strategy']
        mu_val = row['mu']
        f_acc = f"{row['final_accuracy']*100:.2f}%"
        b_acc = f"{row['best_accuracy']*100:.2f}%"
        std_acc = f"{row['accuracy_std']*100:.2f}%"
        
        row_data = [str(alpha_val), str(strat_val), str(mu_val), f_acc, b_acc, std_acc]
        for col_idx, text in enumerate(row_data):
            cell = table2.cell(row_idx + 1, col_idx)
            cell.text = text
            set_cell_margins(cell)
            if (row_idx + 1) % 2 == 1:
                set_cell_shading(cell, "F2F2F2")
            cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
            
    p_cap2 = add_paragraph_with_spacing(doc, "Table 2: RetinaMNIST Sweep Results compiled across concentration parameters alpha and regularization weights mu.", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=6, space_after=12)
    p_cap2.runs[0].font.italic = True
    
    # Embed Figures 1-4 for RetinaMNIST (renumbered figures)
    for fig_file, fig_cap in [
        ("results/fig1_convergence_curves.png", "Figure 6: Convergence curves showing global test accuracy vs. communication rounds under different alpha values."),
        ("results/fig2_accuracy_heatmap.png", "Figure 7: Heatmap illustrating final global test accuracy across the grid parameters alpha and mu."),
        ("results/fig3_fairness_comparison.png", "Figure 8: Fairness metrics comparing client accuracy standard deviations and worst-client performance."),
        ("results/fig4_phase_transition.png", "Figure 9: Phase transition analysis representing the gains/losses of FedProx over standard FedAvg.")
    ]:
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(12)
        p_img.paragraph_format.space_after = Pt(4)
        p_img.add_run().add_picture(fig_file, width=Inches(4.8))
        p_cap = add_paragraph_with_spacing(doc, fig_cap, align=WD_ALIGN_PARAGRAPH.CENTER)
        p_cap.runs[0].font.italic = True
        
    add_heading_with_spacing(doc, "3. IDRiD Clinical Sweep Results & Statistical Underpower Analysis", level=2)
    res_3 = (
        "We scaled the sweep to the actual IDRiD clinical scans. Under moderate skew (α=0.3), adding the proximal penalty (μ=1.0) "
        "on seed 42 helped stabilize training: the client-to-client standard deviation dropped from 0.0520 to 0.0159. However, when "
        "we look at the average final accuracy across all configurations, the improvements are small and easily drowned out "
        "by seed-to-seed variance. A power analysis highlights this issue. With a mean accuracy difference of Δ=0.010 and a "
        "seed standard deviation of σ=0.083, the Cohen's d effect size is a very small 0.1205. To detect this difference "
        "with standard statistical confidence (p < 0.05 at 80% power) would require running 1,082 random seeds per configuration. "
        "This suggests that the small 413-image IDRiD sweep is simply underpowered, which is what led us to use the combined "
        "IDRiD+APTOS dataset."
    )
    add_paragraph_with_spacing(doc, res_3)
    
    df_id = pd.read_csv('/home/shivansh/Desktop/Antigravity /projects/dibetic_retinopathy2/results/experiment_summary.csv')
    df_id = df_id.sort_values(by=['alpha', 'mu', 'seed']).reset_index(drop=True)
    
    # TABLE 3: IDRiD Results
    table3 = doc.add_table(rows=len(df_id) + 1, cols=7)
    table3.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(table3)
    
    headers3 = ["Alpha", "Mu", "Seed", "Strategy", "Final Global Acc", "Best Global Acc", "Client Std"]
    for i, h_text in enumerate(headers3):
        cell = table3.cell(0, i)
        cell.text = h_text
        set_cell_shading(cell, "003366")
        set_cell_margins(cell)
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        cell.paragraphs[0].runs[0].font.bold = True
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        
    for row_idx, row in df_id.iterrows():
        alpha_val = row['alpha']
        mu_val = row['mu']
        seed_val = row['seed']
        strat_val = row['strategy']
        f_acc = f"{row['final_global_accuracy']*100:.2f}%"
        b_acc = f"{row['best_global_accuracy']*100:.2f}%"
        std_acc = f"{row['local_on_test_accuracy_std']*100:.2f}%"
        
        row_data = [str(alpha_val), str(mu_val), str(seed_val), str(strat_val), f_acc, b_acc, std_acc]
        for col_idx, text in enumerate(row_data):
            cell = table3.cell(row_idx + 1, col_idx)
            cell.text = text
            set_cell_margins(cell)
            if (row_idx + 1) % 2 == 1:
                set_cell_shading(cell, "F2F2F2")
            cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
            
    p_cap3 = add_paragraph_with_spacing(doc, "Table 3: IDRiD Clinical Sweep Results across concentration parameters alpha, seeds, and proximal penalty weights mu.", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=6, space_after=12)
    p_cap3.runs[0].font.italic = True
    
    # Embed Figures 5 & 6 (Client Sample Distribution and Skew) (renumbered)
    for fig_file, fig_cap in [
        ("results/fig5_client_sample_distribution.png", "Figure 10: Sample size skew and volume distribution among hospital client nodes under small alpha values."),
        ("results/class_distribution_alpha_0.05.png", "Figure 11: Dirichlet-skewed class allocation across hospital nodes under small alpha (alpha = 0.05).")
    ]:
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(12)
        p_img.paragraph_format.space_after = Pt(4)
        p_img.add_run().add_picture(fig_file, width=Inches(4.8))
        p_img_cap = add_paragraph_with_spacing(doc, fig_cap, align=WD_ALIGN_PARAGRAPH.CENTER)
        p_img_cap.runs[0].font.italic = True
        
    add_heading_with_spacing(doc, "4. Combined IDRiD + APTOS Scaled Sweep Results", level=2)
    res_4 = (
        "To address this underpowering, we ran a scaled federated trial using a combined 4,075-image IDRiD+APTOS dataset. "
        "We must emphasize that this is a preliminary, single-configuration run (α=0.1, seed=42) from an in-progress "
        "sweep; we cannot draw broad conclusions until the full multi-seed run is complete. That caveat aside, this "
        "larger trial reached a peak global accuracy of 55.34%, matching the centralized baseline. This is a promising "
        "early sign that scaling up the data volume allows federated learning to recover centralized performance levels."
    )
    add_paragraph_with_spacing(doc, res_4)
    
    df_comb = pd.read_csv('/home/shivansh/Desktop/Antigravity /projects/dibetic_retinopathy2/results/combined_experiment_summary.csv')
    
    # TABLE 4: Combined Sweep Results
    table4 = doc.add_table(rows=len(df_comb) + 1, cols=7)
    table4.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(table4)
    
    headers4 = ["Alpha", "Mu", "Seed", "Strategy", "Final Global Acc", "Best Global Acc", "Client Std"]
    for i, h_text in enumerate(headers4):
        cell = table4.cell(0, i)
        cell.text = h_text
        set_cell_shading(cell, "003366")
        set_cell_margins(cell)
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        cell.paragraphs[0].runs[0].font.bold = True
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        
    for row_idx, row_comb in df_comb.iterrows():
        row_data_comb = [
            str(row_comb['alpha']),
            str(row_comb['mu']),
            str(row_comb['seed']),
            str(row_comb['strategy']),
            f"{row_comb['final_global_accuracy']*100:.2f}%",
            f"{row_comb['best_global_accuracy']*100:.2f}%",
            f"{row_comb['local_on_test_accuracy_std']*100:.2f}%"
        ]
        for col_idx, text in enumerate(row_data_comb):
            cell = table4.cell(row_idx + 1, col_idx)
            cell.text = text
            set_cell_margins(cell)
            cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        
    p_cap4 = add_paragraph_with_spacing(doc, "Table 4: Combined IDRiD + APTOS Scaled Sweep Results, illustrating preliminary accuracy restoration to centralized levels.", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=6, space_after=12)
    p_cap4.runs[0].font.italic = True
    
    add_heading_with_spacing(doc, "5. Honest SCAFFOLD Debugging Analysis", level=2)
    res_5 = (
        "Our initial sweeps hit a wall: SCAFFOLD remained flat at 43.50% accuracy across all α values. We traced this to two bugs "
        "in our implementation. First, the weight exchange function was omitting BatchNorm running statistics (running mean and variance), "
        "which meant the model evaluated on random initializations. Second, the signature parameters for updating the global "
        "and client control variates were swapped, applying the drift correction with the wrong sign. "
        "Fixing these bugs stabilized the algorithm. As shown in Table 2, the corrected SCAFFOLD achieved final average accuracies "
        "of 48.50% (α=0.05), 48.83% (α=0.3), and 48.00% (α=1.0). However, at α=0.1, SCAFFOLD collapsed to a final average accuracy "
        "of 23.33% (though it reached a peak of 47.50% during training). This indicates that while the structural bugs are fixed, "
        "SCAFFOLD remains highly sensitive to local hyperparameter choices under certain skew levels, an anomaly we are still investigating."
    )
    add_paragraph_with_spacing(doc, res_5)
    
    # --- SECTION V: CONCLUSION & FUTURE WORK ---
    add_heading_with_spacing(doc, "Section V: Conclusion & Future Work", level=1, space_before=18)
    
    conclusion_text = (
        "This study maps out where proximal regularization helps and where it gets in the way when training federated models on skewed "
        "diabetic retinopathy datasets. The experiments show a clear phase transition: tight regularization hurts performance "
        "under severe data skew but offers a solid 4.58-point improvement under moderate skew. More importantly for clinical use, "
        "FedProx acts as a fairness stabilizer, reducing the performance gap between hospitals and boosting the worst-performing "
        "client's accuracy by up to 27.69%. We also debugged the SCAFFOLD implementation, showing that while control variates "
        "correct client drift in theory, they can be highly sensitive to hyperparameters in practice. Finally, our power analysis "
        "suggests that small clinical datasets are statistically underpowered, pointing to the necessity of larger, combined "
        "cohorts like the IDRiD+APTOS pipeline to confirm these optimization behaviors."
    )
    add_paragraph_with_spacing(doc, conclusion_text)
    
    # --- REFERENCES ---
    add_heading_with_spacing(doc, "References", level=1, space_before=18)
    
    references = [
        "[1] B. McMahan, E. Moore, D. Ramage, S. Hampson, and B. A. y Arcas, \"Communication-efficient learning of deep networks from decentralized data,\" in International Conference on Artificial Intelligence and Statistics, 2017, pp. 1273-1282.",
        "[2] T. Li, A. K. Sahu, M. Zaheer, M. Sanjabi, A. Talwalkar, and V. Smith, \"Federated optimization in heterogeneous networks,\" Proceedings of Machine Learning and Systems, vol. 2, pp. 429-450, 2020.",
        "[3] S. P. Karimireddy, S. Kale, M. Mohri, S. Reddi, S. U. Stich, and A. T. Suresh, \"SCAFFOLD: Stochastic controlled averaging for federated learning,\" in International Conference on Machine Learning, 2020, pp. 5132-5143.",
        "[4] T. M. Hsu, H. Qi, and M. Brown, \"Measuring the effects of non-identically distributed data on federated learning,\" arXiv preprint arXiv:1909.06335, 2019.",
        "[5] Q. Li, Y. Diao, Q. Chen, and B. He, \"Federated learning on non-iid data: An empirical study,\" arXiv preprint arXiv:2106.06843, 2021.",
        "[6] J. Yang, R. Shi, D. Wei, Z. Liu, L. Zhao, B. Ke, and Y. Wang, \"MedMNIST v2: A large-scale lightweight benchmark for 2D and 3D biomedical image classification,\" Scientific Data, vol. 10, no. 1, p. 17, 2023.",
        "[7] S. Mohan et al., \"Federated learning for diabetic retinopathy detection using clinical fundus images,\" Journal of Biomedical Informatics, vol. 142, p. 104373, 2023."
    ]
    for ref in references:
        add_paragraph_with_spacing(doc, ref, space_before=3, space_after=6, align=WD_ALIGN_PARAGRAPH.LEFT)

    # --- SAVE DOCUMENT ---
    output_path = "/home/shivansh/Desktop/Antigravity /projects/dibetic_retinopathy2/report_draft.docx"
    print(f"Saving report to {output_path}...")
    doc.save(output_path)
    print("Report saved successfully in DOCX format.")
    
    # --- CONVERT TO PDF ---
    print("Converting DOCX to PDF using LibreOffice...")
    cmd = [
        "libreoffice", "--headless",
        "--convert-to", "pdf",
        "report_draft.docx"
    ]
    try:
        res = subprocess.run(cmd, cwd="/home/shivansh/Desktop/Antigravity /projects/dibetic_retinopathy2", check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("PDF conversion completed successfully.")
        print(res.stdout.decode())
    except subprocess.CalledProcessError as e:
        print("ERROR converting to PDF:")
        print(e.stderr.decode())
        sys.exit(1)

if __name__ == "__main__":
    main()
