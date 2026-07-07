import urllib.request
import os

def render_kroki_post(text, diagram_type, output_path):
    url = f"https://kroki.io/{diagram_type}/png"
    print(f"POSTing to {url} ...")
    req = urllib.request.Request(
        url, 
        data=text.encode('utf-8'), 
        headers={'Content-Type': 'text/plain', 'User-Agent': 'Mozilla/5.0'}
    )
    try:
        with urllib.request.urlopen(req) as response:
            with open(output_path, 'wb') as f:
                f.write(response.read())
        print(f"SUCCESS: Rendered {diagram_type} to {output_path}")
    except Exception as e:
        print(f"ERROR: {e}")

def main():
    mermaid_code = """
    graph LR
        P1["Phase 1: RetinaMNIST<br>• Controlled Synthetic Benchmark<br>• 1,080 Resized Images (28x28)<br>• Custom 3-Layer RetinaCNN<br>• Parameter Sweep (alpha & mu)"]
        P2["Phase 1B: IDRiD Only<br>• Real Clinical Fundus Scans<br>• 413 High-Res Patient Images<br>• EfficientNet-B0 Backbone<br>• High Seed-to-Seed Variance"]
        P3["Phase 2: IDRiD + APTOS<br>• Combined Large-scale Clinical Pipeline<br>• 4,075 Clinical Patient Images<br>• Multi-Silo Scaling Verification<br>• Power Restored (Beta Locked)"]

        P1 --> |Clinical Validation| P2
        P2 --> |Scale Resolution| P3

        classDef boxStyle fill:#EBF5FB,stroke:#2E86C1,stroke-width:2px,color:#1B4F72,font-weight:bold;
        classDef boxStyle2 fill:#E8F8F5,stroke:#27AE60,stroke-width:2px,color:#196F3D,font-weight:bold;
        classDef boxStyle3 fill:#FEF9E7,stroke:#D35400,stroke-width:2px,color:#A04000,font-weight:bold;
        
        class P1 boxStyle;
        class P2 boxStyle2;
        class P3 boxStyle3;
    """
    render_kroki_post(mermaid_code, "mermaid", "test_mermaid_journey.png")

if __name__ == "__main__":
    main()
