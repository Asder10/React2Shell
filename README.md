
<div align="center">

```
    ██████╗ ███████╗ █████╗  ██████╗████████╗██████╗ ███████╗██╗  ██╗███████╗██╗     ██╗
    ██╔══██╗██╔════╝██╔══██╗██╔════╝╚══██╔══╝╚════██╗██╔════╝██║  ██║██╔════╝██║     ██║
    ██████╔╝█████╗  ███████║██║        ██║    █████╔╝███████╗███████║█████╗  ██║     ██║
    ██╔══██╗██╔══╝  ██╔══██║██║        ██║   ██╔═══╝ ╚════██║██╔══██║██╔══╝  ██║     ██║
    ██║  ██║███████╗██║  ██║╚██████╗   ██║   ███████╗███████║██║  ██║███████╗███████╗███████╗
    ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝ ╚═════╝   ╚═╝   ╚══════╝╚══════╝╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝
```

</div>

<div align="center">

**An exploitation framework for CVE-2025-55182 (Next.js/React RCE).**

</div>

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.0-red?style=for-the-badge)
![License](https://img.shields.io/badge/license-MIT-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/python-3.9%2B-green?style=for-the-badge)

</div>

---

### **Table of Contents**
- [About The Project](#about-the-project)
- [Technical Deep Dive](#technical-deep-dive)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)
- [Key Features](#key-features)
- [Disclaimer](#disclaimer)
- [Credits](#credits)

---

### **About The Project**

**React2Shell** is a comprehensive command-line framework designed to scan for and exploit **CVE-2025-55182**, a critical pre-authentication Remote Code Execution (RCE) vulnerability affecting applications using Next.js/React Server Functions.

This tool provides security professionals and researchers with the necessary utilities to test, verify, and understand the impact of this vulnerability in a controlled and authorized environment.

---

### **Technical Deep Dive**

For a detailed technical breakdown of the CVE-2025-55182 vulnerability, including its root cause and exploitation mechanics, please refer to the [**explanation.md**](./explanation.md) file included in this repository.

---

### **Getting Started**

Follow these instructions to get a local copy up and running.

#### **Prerequisites**
- Python 3.9 or higher
- `git` installed on your system

#### **Installation**

Two installation methods are available. The package installation is highly recommended for ease of use.

1.  **As a System Package (Recommended)**
    ```bash
    # Clone the repository
    git clone https://github.com/BlackTechX011/React2Shell
    
    # Navigate into the directory
    cd React2Shell
    
    # Install the tool globally using pip
    pip install .
    
    # Verify the installation
    react2shell --help
    ```

2.  **Manual Installation**
    ```bash
    # Clone the repository
    git clone https://github.com/BlackTechX011/React2Shell
    
    # Navigate into the directory
    cd React2Shell
    
    # Install required dependencies
    pip install -r requirements.txt
    
    # Run the tool directly
    python react2shell.py --help
    ```

---

### **Usage**

React2Shell offers a flexible command-line interface for scanning, exploitation, and reporting.

**Quick Start Example:**
```bash
# Scan a single target for the vulnerability
react2shell -u https://target.com
```

For a complete list of commands, advanced options, and detailed usage examples, please consult the official [**usage.md**](./usage.md) documentation.

---

### **Key Features**

-   **High-Fidelity Scanning**: A robust, multi-threaded scanner to quickly identify vulnerable hosts from a large list of targets.
-   **Interactive Shell**: A full-featured interactive shell to execute commands on a compromised target, facilitating post-exploitation.
-   **WAF Evasion**: Integrated techniques such as junk data injection and advanced payload construction to bypass common security filters.
-   **Stealth Mode**: Employs randomized request delays and User-Agent rotation to minimize detection during scanning and exploitation.
-   **Professional Reporting**: Generate scan reports in multiple formats, including HTML, JSON, and CSV, for documentation and analysis.

---

### **Disclaimer**

> [!WARNING]
> This tool is provided for **educational and authorized security testing purposes ONLY**. Running this tool against systems for which you do not have explicit, written permission is illegal. The author is not responsible for any damage or legal consequences resulting from the misuse of this framework. By downloading or using this software, you agree to take full responsibility for your actions.

---

### **Credits**

-   This framework was developed and packaged by **@BlackTechX011**.
-   The core vulnerability research and initial proof-of-concept were conducted by **[@maple3142](https://x.com/maple3142)**. Their work was instrumental in understanding this vulnerability.
