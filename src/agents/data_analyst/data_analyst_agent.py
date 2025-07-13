import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
import uuid
from datetime import datetime
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import tempfile
import numpy as np

class DataAnalystAgent:
    def __init__(self, user_id):
        self.user_id = user_id

    def _clean_nan_values(self, obj):
        """Recursively replace NaN values with None to make JSON serializable."""
        if isinstance(obj, dict):
            return {key: self._clean_nan_values(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._clean_nan_values(item) for item in obj]
        elif isinstance(obj, (float, np.floating)) and np.isnan(obj):
            return None
        elif isinstance(obj, (int, np.integer)) and np.isnan(obj):
            return None
        else:
            return obj

    def analyze(self, file_bytes):
        try:
            # Try to detect file type and read accordingly
            try:
                # First try Excel
                df = pd.read_excel(io.BytesIO(file_bytes))
            except Exception as excel_error:
                try:
                    # If Excel fails, try CSV
                    df = pd.read_csv(io.BytesIO(file_bytes))
                except Exception as csv_error:
                    # If both fail, try to determine from file content or raise error
                    return {
                        "error": f"Unable to read file. Tried Excel and CSV formats. Excel error: {str(excel_error)}, CSV error: {str(csv_error)}",
                        "report_id": str(uuid.uuid4()),
                        "created_at": datetime.now().isoformat(),
                    }
            
            # Handle empty dataframe
            if df.empty:
                return {
                    "error": "The uploaded file contains no data.",
                    "report_id": str(uuid.uuid4()),
                    "created_at": datetime.now().isoformat(),
                }
            
            desc = df.describe(include='all').to_dict()
            # Clean NaN values from description
            desc = self._clean_nan_values(desc)
            
            plots = {}
            # Histograms
            for col in df.select_dtypes(include='number').columns:
                fig, ax = plt.subplots()
                df[col].hist(ax=ax)
                ax.set_title(f'Histogram of {col}')
                buf = io.BytesIO()
                plt.savefig(buf, format='png')
                buf.seek(0)
                plots[f"hist_{col}"] = base64.b64encode(buf.read()).decode('utf-8')
                plt.close(fig)
            # Box plots
            for col in df.select_dtypes(include='number').columns:
                fig, ax = plt.subplots()
                sns.boxplot(y=df[col], ax=ax)
                ax.set_title(f'Boxplot of {col}')
                buf = io.BytesIO()
                plt.savefig(buf, format='png')
                buf.seek(0)
                plots[f"box_{col}"] = base64.b64encode(buf.read()).decode('utf-8')
                plt.close(fig)
            # Scatter plots (for pairs of numeric columns)
            num_cols = df.select_dtypes(include='number').columns
            for i, col1 in enumerate(num_cols):
                for col2 in num_cols[i+1:]:
                    fig, ax = plt.subplots()
                    ax.scatter(df[col1], df[col2], alpha=0.5)
                    ax.set_xlabel(col1)
                    ax.set_ylabel(col2)
                    ax.set_title(f'Scatter: {col1} vs {col2}')
                    buf = io.BytesIO()
                    plt.savefig(buf, format='png')
                    buf.seek(0)
                    plots[f"scatter_{col1}_{col2}"] = base64.b64encode(buf.read()).decode('utf-8')
                    plt.close(fig)
            # Correlation heatmap
            if len(num_cols) > 1:
                fig, ax = plt.subplots(figsize=(8, 6))
                corr = df[num_cols].corr()
                # Clean NaN values from correlation matrix
                corr = corr.fillna(0)  # Replace NaN with 0 for correlation
                sns.heatmap(corr, annot=True, cmap='coolwarm', ax=ax)
                ax.set_title('Correlation Heatmap')
                buf = io.BytesIO()
                plt.savefig(buf, format='png')
                buf.seek(0)
                plots['correlation_heatmap'] = base64.b64encode(buf.read()).decode('utf-8')
                plt.close(fig)
            # Time series forecasting (if a datetime and numeric column exist)
            forecast = None
            date_cols = df.select_dtypes(include=['datetime', 'datetimetz']).columns
            if len(date_cols) > 0 and len(num_cols) > 0:
                date_col = date_cols[0]
                value_col = num_cols[0]
                ts = df[[date_col, value_col]].dropna().sort_values(date_col)
                ts = ts.set_index(date_col)[value_col]
                if len(ts) > 10:
                    try:
                        model = ExponentialSmoothing(ts, trend='add', seasonal=None)
                        fit = model.fit()
                        forecast_vals = fit.forecast(steps=5)
                        forecast = forecast_vals.to_dict()
                        # Clean NaN values from forecast
                        forecast = self._clean_nan_values(forecast)
                        # Plot forecast
                        fig, ax = plt.subplots()
                        ts.plot(ax=ax, label='Actual')
                        forecast_vals.plot(ax=ax, label='Forecast', style='--')
                        ax.set_title(f'Forecast for {value_col}')
                        ax.legend()
                        buf = io.BytesIO()
                        plt.savefig(buf, format='png')
                        buf.seek(0)
                        plots['forecast'] = base64.b64encode(buf.read()).decode('utf-8')
                        plt.close(fig)
                    except Exception as e:
                        forecast = f"Forecasting error: {e}"
            # Natural language summary
            summary = self.generate_summary(df, desc, forecast)
            # Compose report
            report = {
                "description": desc,
                "plots": plots,
                "forecast": forecast,
                "summary": summary,
                "report_id": str(uuid.uuid4()),
                "created_at": datetime.now().isoformat(),
            }
            return report
        except Exception as e:
            return {
                "error": f"Error analyzing data: {str(e)}",
                "report_id": str(uuid.uuid4()),
                "created_at": datetime.now().isoformat(),
            }

    def generate_summary(self, df, desc, forecast):
        lines = []
        lines.append(f"The dataset contains {df.shape[0]} rows and {df.shape[1]} columns.")
        for col in df.columns:
            dtype = df[col].dtype
            lines.append(f"Column '{col}' is of type {dtype}.")
            if str(dtype).startswith('float') or str(dtype).startswith('int'):
                mean_val = desc[col].get('mean', 'N/A')
                std_val = desc[col].get('std', 'N/A')
                min_val = desc[col].get('min', 'N/A')
                max_val = desc[col].get('max', 'N/A')
                # Handle None values from NaN cleaning
                mean_val = 'N/A' if mean_val is None else mean_val
                std_val = 'N/A' if std_val is None else std_val
                min_val = 'N/A' if min_val is None else min_val
                max_val = 'N/A' if max_val is None else max_val
                lines.append(f"  Mean: {mean_val}, Std: {std_val}, Min: {min_val}, Max: {max_val}")
            elif str(dtype).startswith('object'):
                top_val = desc[col].get('top', 'N/A')
                freq_val = desc[col].get('freq', 'N/A')
                # Handle None values from NaN cleaning
                top_val = 'N/A' if top_val is None else top_val
                freq_val = 'N/A' if freq_val is None else freq_val
                lines.append(f"  Most frequent: {top_val} (count: {freq_val})")
        if forecast:
            lines.append(f"Forecast for next 5 periods: {forecast}")
        return '\n'.join(lines)

    def generate_pdf_report(self, report, file_path):
        c = canvas.Canvas(file_path, pagesize=letter)
        width, height = letter
        c.setFont("Helvetica", 12)
        c.drawString(30, height - 30, f"Data Analyst Report - {report.get('created_at', '')}")
        c.drawString(30, height - 50, f"Report ID: {report.get('report_id', '')}")
        # Summary
        text = c.beginText(30, height - 80)
        for line in report['summary'].split('\n'):
            text.textLine(line)
        c.drawText(text)
        # Plots (show up to 3 for brevity)
        y = height - 200
        for i, (plot_name, plot_b64) in enumerate(report['plots'].items()):
            if i >= 3:
                break
            img_bytes = base64.b64decode(plot_b64)
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_img:
                tmp_img.write(img_bytes)
                tmp_img.flush()
                c.drawImage(ImageReader(tmp_img.name), 30, y - 120, width=200, height=120)
            c.drawString(240, y - 60, plot_name)
            y -= 140
        c.save()

    def get_agent(self):
        # Returns a callable agent interface for the supervisor orchestrator
        def agent_interface(input_data):
            # Expect input_data to be a dict with 'file_bytes' or 'file_url' or 'data' (base64)
            # For chat, expect a text command and optionally a file (to be handled by orchestrator)
            if isinstance(input_data, dict) and ('file_bytes' in input_data or 'data' in input_data):
                file_bytes = input_data.get('file_bytes') or input_data.get('data')
                return self.analyze(file_bytes)
            elif isinstance(input_data, str):
                # If a text command, respond with instructions
                return {
                    'message': "To analyze data, please upload an Excel (.xlsx/.xls) or CSV file or provide a data source."
                }
            else:
                return {'message': 'Invalid input for Data Analyst Agent.'}
        
        # Create an agent object with the required attributes
        class AgentWrapper:
            def __init__(self, func):
                self.func = func
                self.name = "DataAnalystAgent"
            
            def __call__(self, *args, **kwargs):
                return self.func(*args, **kwargs)
        
        return AgentWrapper(agent_interface)

    def get_description(self):
        return "Analyzes uploaded Excel and CSV files and generates reports with plots, statistics, and forecasts." 