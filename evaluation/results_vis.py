"""
Results Visualization & Statistical Analysis
===========================================
Generates publication-quality charts and statistical analysis
for thesis Results and Discussion sections
"""

import json
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
import pandas as pd
from scipy import stats

# Set publication style
plt.style.use('seaborn-v0_8-paper')
sns.set_palette("husl")

class ResultsVisualizer:
    """Generate visualizations and statistical analysis"""
    
    def __init__(self, results_file='evaluation_results.json'):
        with open(results_file, 'r') as f:
            self.results = json.load(f)
        
        # Create output directory
        self.output_dir = Path('evaluation_results')
        self.output_dir.mkdir(exist_ok=True)
    
    def plot_intent_detection_metrics(self):
        """Plot intent detection performance"""
        metrics = self.results['intent_detection']
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # Subplot 1: Bar chart of metrics
        metric_names = ['Accuracy', 'Precision', 'Recall', 'F1-Score']
        metric_values = [
            metrics['accuracy'],
            metrics['precision'],
            metrics['recall'],
            metrics['f1_score']
        ]
        
        colors = ['#2ecc71', '#3498db', '#9b59b6', '#e74c3c']
        bars = ax1.bar(metric_names, metric_values, color=colors, alpha=0.8)
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.3f}',
                    ha='center', va='bottom', fontsize=10)
        
        ax1.set_ylim([0, 1.1])
        ax1.set_ylabel('Score', fontsize=12)
        ax1.set_title('Intent Detection Metrics', fontsize=14, fontweight='bold')
        ax1.grid(axis='y', alpha=0.3)
        
        # Subplot 2: Confusion matrix visualization
        correct = metrics['correct']
        total = metrics['total_cases']
        incorrect = total - correct
        
        confusion_data = [[correct, incorrect]]
        ax2.imshow(confusion_data, cmap='RdYlGn', aspect='auto', vmin=0, vmax=total)
        
        ax2.set_xticks([0, 1])
        ax2.set_xticklabels(['Correct', 'Incorrect'])
        ax2.set_yticks([0])
        ax2.set_yticklabels(['Predictions'])
        ax2.set_title(f'Classification Results\n({correct}/{total} correct)', 
                     fontsize=14, fontweight='bold')
        
        # Add text annotations
        for i in range(2):
            value = [correct, incorrect][i]
            ax2.text(i, 0, f'{value}\n({value/total:.1%})',
                    ha='center', va='center', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'intent_detection_metrics.png', dpi=300, bbox_inches='tight')
        print(f"✓ Saved: intent_detection_metrics.png")
        plt.close()
    
    def plot_entity_extraction_breakdown(self):
        """Plot entity extraction performance breakdown"""
        metrics = self.results['entity_extraction']
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # Subplot 1: Accuracy metrics
        accuracy_data = {
            'Exact Match': metrics['correct'],
            'Partial Match': metrics['partial'],
            'Missed': metrics['missed']
        }
        
        colors = ['#27ae60', '#f39c12', '#e74c3c']
        wedges, texts, autotexts = ax1.pie(
            accuracy_data.values(),
            labels=accuracy_data.keys(),
            autopct='%1.1f%%',
            colors=colors,
            startangle=90
        )
        
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        ax1.set_title('Entity Extraction Results\n(Field-level Accuracy)', 
                     fontsize=14, fontweight='bold')
        
        # Subplot 2: Bar comparison
        metric_names = ['Accuracy', 'Coverage']
        metric_values = [metrics['accuracy'], metrics['coverage']]
        
        bars = ax2.bar(metric_names, metric_values, color=['#3498db', '#9b59b6'], alpha=0.8)
        
        for bar in bars:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.3f}',
                    ha='center', va='bottom', fontsize=12, fontweight='bold')
        
        ax2.set_ylim([0, 1.1])
        ax2.set_ylabel('Score', fontsize=12)
        ax2.set_title('Extraction Performance Metrics', fontsize=14, fontweight='bold')
        ax2.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'entity_extraction_breakdown.png', dpi=300, bbox_inches='tight')
        print(f"✓ Saved: entity_extraction_breakdown.png")
        plt.close()
    
    def plot_contract_generation_quality(self):
        """Plot contract generation quality scores"""
        metrics = self.results['contract_generation']
        scores = metrics.get('scores', [])
        
        if not scores:
            print("⚠ No contract generation scores available")
            return
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # Subplot 1: Individual contract scores
        contracts = [f'Contract {i+1}' for i in range(len(scores))]
        colors = ['#2ecc71' if s >= 0.8 else '#f39c12' if s >= 0.6 else '#e74c3c' for s in scores]
        
        bars = ax1.bar(contracts, scores, color=colors, alpha=0.8)
        
        for bar in bars:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.2f}',
                    ha='center', va='bottom', fontsize=10)
        
        ax1.axhline(y=metrics['average_completeness'], color='red', 
                   linestyle='--', label=f'Average: {metrics["average_completeness"]:.3f}')
        ax1.set_ylim([0, 1.1])
        ax1.set_ylabel('Completeness Score', fontsize=12)
        ax1.set_title('Contract Generation Quality by Test', fontsize=14, fontweight='bold')
        ax1.legend()
        ax1.grid(axis='y', alpha=0.3)
        
        # Subplot 2: Success rate
        success = metrics['successful_generations']
        total = metrics['total_contracts_tested']
        failed = total - success
        
        ax2.pie([success, failed], 
               labels=['Successful', 'Failed'],
               autopct='%1.1f%%',
               colors=['#27ae60', '#e74c3c'],
               startangle=90)
        
        ax2.set_title(f'Generation Success Rate\n({success}/{total} contracts)', 
                     fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'contract_generation_quality.png', dpi=300, bbox_inches='tight')
        print(f"✓ Saved: contract_generation_quality.png")
        plt.close()
    
    def plot_performance_comparison(self):
        """Plot system performance metrics"""
        metrics = self.results['performance']
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        operations = [
            'Intent\nDetection',
            'Entity\nExtraction',
            'Contract\nGeneration'
        ]
        
        times = [
            metrics['avg_intent_detection_ms'],
            metrics['entity_extraction_ms'],
            metrics['contract_generation_ms']
        ]
        
        colors = ['#3498db', '#9b59b6', '#e74c3c']
        bars = ax.barh(operations, times, color=colors, alpha=0.8)
        
        # Add value labels
        for i, bar in enumerate(bars):
            width = bar.get_width()
            ax.text(width, bar.get_y() + bar.get_height()/2.,
                   f'{width:.2f} ms',
                   ha='left', va='center', fontsize=11, fontweight='bold')
        
        ax.set_xlabel('Response Time (milliseconds)', fontsize=12)
        ax.set_title('System Performance: Operation Response Times', 
                    fontsize=14, fontweight='bold')
        ax.grid(axis='x', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'performance_comparison.png', dpi=300, bbox_inches='tight')
        print(f"✓ Saved: performance_comparison.png")
        plt.close()
    
    def plot_overall_system_performance(self):
        """Create comprehensive system performance radar chart"""
        # Normalize all metrics to 0-1 scale
        metrics = {
            'Intent\nAccuracy': self.results['intent_detection']['accuracy'],
            'Entity\nExtraction': self.results['entity_extraction']['accuracy'],
            'Contract\nQuality': self.results['contract_generation']['average_completeness'],
            'F1-Score': self.results['intent_detection']['f1_score'],
            'Recall': self.results['intent_detection']['recall'],
            'Precision': self.results['intent_detection']['precision']
        }
        
        categories = list(metrics.keys())
        values = list(metrics.values())
        
        # Radar chart
        angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
        values += values[:1]
        angles += angles[:1]
        
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
        
        ax.plot(angles, values, 'o-', linewidth=2, color='#3498db', label='System Performance')
        ax.fill(angles, values, alpha=0.25, color='#3498db')
        
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories, fontsize=11)
        ax.set_ylim(0, 1)
        ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
        ax.set_yticklabels(['0.2', '0.4', '0.6', '0.8', '1.0'])
        ax.grid(True)
        
        ax.set_title('Overall System Performance Metrics', 
                    fontsize=16, fontweight='bold', pad=20)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'overall_system_performance.png', dpi=300, bbox_inches='tight')
        print(f"✓ Saved: overall_system_performance.png")
        plt.close()
    
    def generate_statistical_analysis(self):
        """Generate statistical analysis report"""
        print("\n" + "="*60)
        print("STATISTICAL ANALYSIS")
        print("="*60)
        
        report = []
        report.append("# Statistical Analysis Report\n")
        
        # 1. Intent Detection Statistics
        report.append("\n## 1. Intent Detection Analysis\n")
        id_metrics = self.results['intent_detection']
        
        report.append(f"- **Sample Size**: {id_metrics['total_cases']} test cases")
        report.append(f"- **Accuracy**: {id_metrics['accuracy']:.4f} ({id_metrics['correct']}/{id_metrics['total_cases']})")
        report.append(f"- **Precision**: {id_metrics['precision']:.4f}")
        report.append(f"- **Recall**: {id_metrics['recall']:.4f}")
        report.append(f"- **F1-Score**: {id_metrics['f1_score']:.4f}")
        
        # Confidence interval for accuracy (binomial)
        n = id_metrics['total_cases']
        p = id_metrics['accuracy']
        ci = 1.96 * np.sqrt(p * (1-p) / n)  # 95% CI
        report.append(f"- **95% Confidence Interval**: [{p-ci:.4f}, {p+ci:.4f}]")
        
        # 2. Entity Extraction Statistics
        report.append("\n## 2. Entity Extraction Analysis\n")
        ee_metrics = self.results['entity_extraction']
        
        report.append(f"- **Total Fields Tested**: {ee_metrics['total_fields']}")
        report.append(f"- **Exact Matches**: {ee_metrics['correct']} ({ee_metrics['correct']/ee_metrics['total_fields']:.2%})")
        report.append(f"- **Partial Matches**: {ee_metrics['partial']} ({ee_metrics['partial']/ee_metrics['total_fields']:.2%})")
        report.append(f"- **Missed**: {ee_metrics['missed']} ({ee_metrics['missed']/ee_metrics['total_fields']:.2%})")
        report.append(f"- **Overall Accuracy**: {ee_metrics['accuracy']:.4f}")
        report.append(f"- **Coverage Rate**: {ee_metrics['coverage']:.4f}")
        
        # 3. Contract Generation Statistics
        report.append("\n## 3. Contract Generation Quality\n")
        cg_metrics = self.results['contract_generation']
        scores = cg_metrics.get('scores', [])
        
        if scores:
            report.append(f"- **Mean Completeness**: {np.mean(scores):.4f}")
            report.append(f"- **Std Deviation**: {np.std(scores):.4f}")
            report.append(f"- **Min Score**: {np.min(scores):.4f}")
            report.append(f"- **Max Score**: {np.max(scores):.4f}")
            report.append(f"- **Success Rate**: {cg_metrics['successful_generations']}/{cg_metrics['total_contracts_tested']} ({cg_metrics['successful_generations']/cg_metrics['total_contracts_tested']:.2%})")
        
        # 4. Performance Statistics
        report.append("\n## 4. Performance Metrics\n")
        perf = self.results['performance']
        
        report.append(f"- **Intent Detection**: {perf['avg_intent_detection_ms']:.2f} ms")
        report.append(f"- **Entity Extraction**: {perf['entity_extraction_ms']:.2f} ms")
        report.append(f"- **Contract Generation**: {perf['contract_generation_ms']:.2f} ms")
        report.append(f"- **Total Avg Response**: {perf['total_avg_response_ms']:.2f} ms")
        
        # System meets <1s response time requirement?
        meets_requirement = perf['total_avg_response_ms'] < 1000
        report.append(f"- **Meets <1s requirement**: {'✓ Yes' if meets_requirement else '✗ No'}")
        
        # 5. Overall System Score
        report.append("\n## 5. Overall System Score\n")
        overall_score = (
            id_metrics['f1_score'] * 0.30 +
            ee_metrics['accuracy'] * 0.25 +
            cg_metrics['average_completeness'] * 0.25 +
            (1 if meets_requirement else 0.5) * 0.20
        )
        
        report.append(f"- **Weighted Overall Score**: {overall_score:.4f} / 1.0")
        report.append(f"  - Intent Detection (30%): {id_metrics['f1_score']:.4f}")
        report.append(f"  - Entity Extraction (25%): {ee_metrics['accuracy']:.4f}")
        report.append(f"  - Generation Quality (25%): {cg_metrics['average_completeness']:.4f}")
        report.append(f"  - Performance (20%): {1 if meets_requirement else 0.5:.4f}")
        
        # Save report
        report_text = '\n'.join(report)
        with open(self.output_dir / 'statistical_analysis.md', 'w') as f:
            f.write(report_text)
        
        print(report_text)
        print(f"\n✓ Saved: statistical_analysis.md")
    
    def generate_comparison_table(self):
        """Generate comparison table for discussion"""
        data = {
            'Metric': [
                'Intent Detection Accuracy',
                'Entity Extraction Accuracy',
                'Contract Generation Quality',
                'F1-Score',
                'Average Response Time (ms)'
            ],
            'Score': [
                f"{self.results['intent_detection']['accuracy']:.3f}",
                f"{self.results['entity_extraction']['accuracy']:.3f}",
                f"{self.results['contract_generation']['average_completeness']:.3f}",
                f"{self.results['intent_detection']['f1_score']:.3f}",
                f"{self.results['performance']['total_avg_response_ms']:.2f}"
            ],
            'Target': ['≥0.90', '≥0.85', '≥0.80', '≥0.85', '<1000'],
            'Status': []
        }
        
        # Determine status
        thresholds = [0.90, 0.85, 0.80, 0.85, 1000]
        for i, (score_str, threshold) in enumerate(zip(data['Score'], thresholds)):
            score = float(score_str)
            if i < 4:  # First 4 are higher-is-better
                status = '✓ Pass' if score >= threshold else '⚠ Needs Improvement'
            else:  # Last one is lower-is-better
                status = '✓ Pass' if score < threshold else '⚠ Needs Improvement'
            data['Status'].append(status)
        
        df = pd.DataFrame(data)
        
        # Save as CSV
        df.to_csv(self.output_dir / 'metrics_comparison.csv', index=False)
        
        # Print formatted table
        print("\n" + "="*60)
        print("METRICS COMPARISON TABLE")
        print("="*60)
        print(df.to_string(index=False))
        print(f"\n✓ Saved: metrics_comparison.csv")
    
    def generate_all_visualizations(self):
        """Generate all visualizations and analyses"""
        print("\n🎨 Generating visualizations and statistical analysis...\n")
        
        self.plot_intent_detection_metrics()
        self.plot_entity_extraction_breakdown()
        self.plot_contract_generation_quality()
        self.plot_performance_comparison()
        self.plot_overall_system_performance()
        
        self.generate_statistical_analysis()
        self.generate_comparison_table()
        
        print(f"\n✅ All visualizations saved to: {self.output_dir}/")
        print("="*60)


# ========================================
# MAIN EXECUTION
# ========================================

if __name__ == "__main__":
    # Check if results file exists
    if not Path('evaluation_results.json').exists():
        print("❌ Error: evaluation_results.json not found!")
        print("Please run the evaluation script first:")
        print("  python evaluate_system.py")
    else:
        visualizer = ResultsVisualizer()
        visualizer.generate_all_visualizations()