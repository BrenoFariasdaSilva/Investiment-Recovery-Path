<div align="center">
  
# [Investiment Recovery Path.](https://github.com/BrenoFariasdaSilva/Investiment-Recovery-Path) <img src="https://github.com/BrenoFariasdaSilva/Investiment-Recovery-Path/blob/main/.assets/Icons/investment.svg"  width="3%" height="3%">

</div>

<div align="center">
  
---

Analyzes cryptocurrency investment portfolios and calculates optimal recovery strategies for assets with negative returns through proportional budget allocation.
  
---

</div>

<div align="center">

![GitHub Code Size in Bytes](https://img.shields.io/github/languages/code-size/BrenoFariasdaSilva/Template-Project)
![GitHub Commits](https://img.shields.io/github/commit-activity/t/BrenoFariasDaSilva/Template-Project/main)
![GitHub Last Commit](https://img.shields.io/github/last-commit/BrenoFariasdaSilva/Template-Project)
![GitHub Forks](https://img.shields.io/github/forks/BrenoFariasDaSilva/Template-Project)
![GitHub Language Count](https://img.shields.io/github/languages/count/BrenoFariasDaSilva/Template-Project)
![GitHub License](https://img.shields.io/github/license/BrenoFariasdaSilva/Template-Project)
![GitHub Stars](https://img.shields.io/github/stars/BrenoFariasdaSilva/Template-Project)
![GitHub Contributors](https://img.shields.io/github/contributors/BrenoFariasdaSilva/Template-Project)
![GitHub Created At](https://img.shields.io/github/created-at/BrenoFariasdaSilva/Template-Project)
![wakatime](https://wakatime.com/badge/github/BrenoFariasdaSilva/Investiment Recovery Path.svg)

</div>

<div align="center">
  
![RepoBeats Statistics](https://repobeats.axiom.co/api/embed/7aab7ac179c13d6489e877d918cd86023ba65c7d.svg "Repobeats analytics image")

</div>

## Table of Contents
- [Investiment Recovery Path. ](#investiment-recovery-path-)
  - [Table of Contents](#table-of-contents)
  - [Introduction](#introduction)
  - [Requirements](#requirements)
  - [Setup](#setup)
    - [Clone the repository](#clone-the-repository)
    - [Python, Pip and Venv](#python-pip-and-venv)
      - [Linux](#linux)
      - [MacOS](#macos)
      - [Windows](#windows)
  - [Run Python Code:](#run-python-code)
    - [Dependencies](#dependencies)
  - [Usage](#usage)
  - [Results](#results)
  - [Contributing](#contributing)
  - [Collaborators](#collaborators)
  - [License](#license)
    - [Apache License 2.0](#apache-license-20)

## Introduction

This Investment Recovery Path Calculator is a Python-based tool that analyzes cryptocurrency investment portfolios from Excel files and calculates optimal recovery strategies for assets with negative returns. The script performs proportional allocation of available budget based on current losses to minimize overall portfolio loss percentage.

**Key Features:**
- Automatic Excel data loading and preprocessing with data cleaning
- Proportional loss-based budget allocation across losing assets
- New loss percentage calculation after hypothetical investment
- Improvement metrics showing expected recovery in percentage points
- Comprehensive output table with investment recommendations
- Detailed logging with timestamps for execution history

## Requirements

- Python >= 3.7
- pandas >= 2.0.0
- numpy >= 1.24.0
- openpyxl >= 3.1.0 (for Excel file reading)
- colorama == 0.4.6 (for terminal coloring)
- Excel file with proper format containing columns: Data, Total Spent - R$, Current Amount - R$, Profit - R$, Profit - %

## Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**. If you have suggestions for improving the code, your insights will be highly welcome.
In order to contribute to this project, please follow the guidelines below or read the [CONTRIBUTING.md](CONTRIBUTING.md) file for more details on how to contribute to this project, as it contains information about the commit standards and the entire pull request process.
Please follow these guidelines to make your contributions smooth and effective:

1. **Set Up Your Environment**: Ensure you've followed the setup instructions in the [Setup](#setup) section to prepare your development environment.

2. **Make Your Changes**:
   - **Create a Branch**: `git checkout -b feature/YourFeatureName`
   - **Implement Your Changes**: Make sure to test your changes thoroughly.
   - **Commit Your Changes**: Use clear commit messages, for example:
     - For new features: `git commit -m "FEAT: Add some AmazingFeature"`
     - For bug fixes: `git commit -m "FIX: Resolve Issue #123"`
     - For documentation: `git commit -m "DOCS: Update README with new instructions"`
     - For refactorings: `git commit -m "REFACTOR: Enhance component for better aspect"`
     - For snapshots: `git commit -m "SNAPSHOT: Temporary commit to save the current state for later reference"`
   - See more about crafting commit messages in the [CONTRIBUTING.md](CONTRIBUTING.md) file.

3. **Submit Your Contribution**:
   - **Push Your Changes**: `git push origin feature/YourFeatureName`
   - **Open a Pull Request (PR)**: Navigate to the repository on GitHub and open a PR with a detailed description of your changes.

4. **Stay Engaged**: Respond to any feedback from the project maintainers and make necessary adjustments to your PR.

5. **Celebrate**: Once your PR is merged, celebrate your contribution to the project!

## Collaborators

We thank the following people who contributed to this project:

<table>
  <tr>
    <td align="center">
      <a href="#" title="defina o titulo do link">
        <img src="https://github.com/BrenoFariasdaSilva.png" width="100px;" alt="My Profile Picture"/><br>
        <sub>
          <b>Breno Farias da Silva</b>
        </sub>
      </a>
    </td>
  </tr>
</table>

## License

### Apache License 2.0

This project is licensed under the [Apache License 2.0](LICENSE). This license permits use, modification, distribution, and sublicense of the code for both private and commercial purposes, provided that the original copyright notice and a disclaimer of warranty are included in all copies or substantial portions of the software. It also requires a clear attribution back to the original author(s) of the repository. For more details, see the [LICENSE](LICENSE) file in this repository.
