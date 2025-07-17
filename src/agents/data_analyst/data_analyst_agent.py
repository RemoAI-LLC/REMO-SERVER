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
from typing import List, Dict, Optional, Annotated
import os
import boto3
import json

# LangGraph imports
from langgraph.prebuilt import create_react_agent
try:
    from langchain_aws import ChatBedrock
except ImportError:
    ChatBedrock = None
from langchain.tools import tool
from langsmith import traceable

class DataAnalystAgent:
    def __init__(self, user_id: str = None):
        """
        Initialize the Data Analysis Agent with tools and persona.
        
        Args:
            user_id: User ID for user-specific functionality
        """
        self.name = "data_analyst_agent"
        self.user_id = user_id
        
        # Bedrock LLM initialization
        model_id = os.getenv("BEDROCK_MODEL_ID", "amazon.nova-lite-v1:0")
        region = os.getenv("AWS_REGION", "us-east-1")
        access_key = os.getenv("AWS_ACCESS_KEY_ID")
        secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        temperature = 0.3
        
        if ChatBedrock:
            self.llm = ChatBedrock(
                model_id=model_id,
                region_name=region,
                model_kwargs={"temperature": temperature}
            )
        else:
            class BedrockLLM:
                def __init__(self, model_id, region, access_key, secret_key, temperature):
                    self.model_id = model_id
                    self.temperature = temperature
                    print(f"[BedrockLLM] Initializing with model_id={model_id}, region={region}")
                    self.client = boto3.client(
                        "bedrock-runtime",
                        region_name=region,
                        aws_access_key_id=access_key,
                        aws_secret_access_key=secret_key,
                    )
                def invoke(self, messages):
                    # Ensure content is a list of objects with 'text' for each message
                    for m in messages:
                        if isinstance(m.get("content"), str):
                            m["content"] = [{"text": m["content"]}]
                        elif isinstance(m.get("content"), list):
                            m["content"] = [c if isinstance(c, dict) else {"text": c} for c in m["content"]]
                    print(f"[BedrockLLM] Invoking model {self.model_id} with messages: {messages}")
                    body = {
                        "messages": messages
                    }
                    try:
                        response = self.client.invoke_model(
                            modelId=self.model_id,
                            body=json.dumps(body),
                            contentType="application/json",
                            accept="application/json"
                        )
                        result = json.loads(response["body"].read())
                        print(f"[BedrockLLM] Response: {str(result)[:200]}")
                        class Result:
                            def __init__(self, content):
                                self.content = content
                        return Result(result.get("completion") or result.get("output", ""))
                    except Exception as e:
                        print(f"[BedrockLLM] ERROR: {e}")
                        raise
            self.llm = BedrockLLM(model_id, region, access_key, secret_key, temperature)
        
        # Define the agent's specialized persona
        self.persona = """You are a Data Analysis Specialist within the Remo AI assistant ecosystem. 
Your expertise is in analyzing data, creating visualizations, and providing actionable insights from datasets.

Your key characteristics:
- **Analytical**: You think critically about data patterns, trends, and relationships
- **Thorough**: You examine data from multiple angles and provide comprehensive analysis
- **Clear**: You explain complex statistical concepts in simple, understandable terms
- **Insightful**: You don't just report numbers - you interpret what they mean
- **Professional**: You maintain a confident, knowledgeable tone while being approachable
- **Helpful**: You guide users through data analysis and suggest next steps

Your capabilities:
- Analyze Excel and CSV files with statistical summaries
- Create meaningful visualizations (histograms, box plots, scatter plots, correlation heatmaps)
- Perform time series forecasting when appropriate
- Generate natural language summaries of data findings
- Identify patterns, outliers, and trends in data
- Provide actionable insights and recommendations

When analyzing data:
1. Always start with a clear overview of the dataset structure
2. Explain what each visualization reveals about the data
3. Highlight any interesting patterns or anomalies you discover
4. Provide context for statistical measures (mean, median, standard deviation)
5. Suggest potential next steps for deeper analysis

When creating visualizations:
1. Choose appropriate chart types for the data and analysis goals
2. Ensure plots are clear and informative
3. Use meaningful titles and labels
4. Consider the story the data is telling

When providing insights:
1. Focus on what the data means, not just what it shows
2. Connect findings to potential business or practical implications
3. Be honest about limitations or uncertainties in the analysis
4. Suggest areas for further investigation when appropriate

IMPORTANT GUIDELINES:
1. **File Upload Required**: You can ONLY analyze data when a user uploads an Excel (.xlsx/.xls) or CSV file. You cannot analyze data without a file.
2. **Tool Usage**: When a user provides a data file, you MUST use the analyze_data_file tool to analyze it.
3. **Comprehensive Analysis**: Always provide complete analysis including descriptive statistics, visualizations, forecasts, and insights.
4. **No File Scenarios**: If a user asks for data analysis but hasn't uploaded a file, respond with helpful guidance about what you can do and how to upload a file.
5. **File Format Support**: You support Excel (.xlsx, .xls) and CSV files only.
6. **Error Handling**: If a file cannot be read or is empty, provide clear, helpful error messages.

When no file is provided:
- Explain what types of analysis you can perform
- Guide users on how to upload their data files
- Suggest what kind of data would be most valuable to analyze
- Offer to help once they have a file ready

Remember: You're part of a larger AI assistant system, so be collaborative and refer users to other specialists when needed. Your goal is to make data analysis accessible and valuable to users of all technical levels."""

        # Create user-specific tool wrappers
        self.tools = self._create_user_specific_tools()
        
        # Create the agent with tools
        self.agent = create_react_agent(
            model=self.llm,
            tools=self.tools,
            prompt=self.persona,
            name="data_analyst_agent"
        )

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
                ts = df[[date_col, value_col]].dropna().sort_values(by=str(date_col))
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
        lines.append(f"📊 **Dataset Overview**")
        lines.append(f"Your dataset contains {df.shape[0]:,} rows and {df.shape[1]} columns, giving us a solid foundation for analysis.")
        lines.append("")
        
        lines.append("🔍 **Column Analysis**")
        for col in df.columns:
            dtype = df[col].dtype
            lines.append(f"**{col}** ({dtype}):")
            
            if str(dtype).startswith('float') or str(dtype).startswith('int'):
                mean_val = desc[col].get('mean', 'N/A')
                std_val = desc[col].get('std', 'N/A')
                min_val = desc[col].get('min', 'N/A')
                max_val = desc[col].get('max', 'N/A')
                median_val = desc[col].get('50%', 'N/A')
                
                # Handle None values from NaN cleaning
                mean_val = 'N/A' if mean_val is None else f"{mean_val:.2f}" if isinstance(mean_val, (int, float)) else str(mean_val)
                std_val = 'N/A' if std_val is None else f"{std_val:.2f}" if isinstance(std_val, (int, float)) else str(std_val)
                min_val = 'N/A' if min_val is None else f"{min_val:.2f}" if isinstance(min_val, (int, float)) else str(min_val)
                max_val = 'N/A' if max_val is None else f"{max_val:.2f}" if isinstance(max_val, (int, float)) else str(max_val)
                median_val = 'N/A' if median_val is None else f"{median_val:.2f}" if isinstance(median_val, (int, float)) else str(median_val)
                
                lines.append(f"  • **Range**: {min_val} to {max_val}")
                lines.append(f"  • **Average**: {mean_val} (median: {median_val})")
                lines.append(f"  • **Variability**: Standard deviation of {std_val}")
                
                # Add insights based on the data
                if mean_val != 'N/A' and std_val != 'N/A':
                    try:
                        mean_float = float(mean_val)
                        std_float = float(std_val)
                        if std_float > mean_float * 0.5:
                            lines.append(f"  • **Insight**: This column shows high variability, suggesting diverse values")
                        elif std_float < mean_float * 0.1:
                            lines.append(f"  • **Insight**: Values are quite consistent with low variability")
                    except:
                        pass
                        
            elif str(dtype).startswith('object'):
                top_val = desc[col].get('top', 'N/A')
                freq_val = desc[col].get('freq', 'N/A')
                unique_count = desc[col].get('unique', 'N/A')
                
                # Handle None values from NaN cleaning
                top_val = 'N/A' if top_val is None else str(top_val)
                freq_val = 'N/A' if freq_val is None else str(freq_val)
                unique_count = 'N/A' if unique_count is None else str(unique_count)
                
                lines.append(f"  • **Most common**: '{top_val}' appears {freq_val} times")
                lines.append(f"  • **Unique values**: {unique_count} different categories")
                
                # Add insights for categorical data
                if unique_count != 'N/A' and freq_val != 'N/A':
                    try:
                        unique_int = int(unique_count)
                        freq_int = int(freq_val)
                        total_rows = df.shape[0]
                        if unique_int < total_rows * 0.1:
                            lines.append(f"  • **Insight**: Low diversity - most values are concentrated in few categories")
                        elif freq_int < total_rows * 0.05:
                            lines.append(f"  • **Insight**: High diversity - no single value dominates")
                    except:
                        pass
        
        lines.append("")
        if forecast:
            lines.append("🔮 **Forecasting**")
            lines.append(f"Based on the time series analysis, here's what we can expect for the next 5 periods:")
            for date, value in forecast.items():
                if isinstance(value, (int, float)):
                    lines.append(f"  • {date}: {value:.2f}")
                else:
                    lines.append(f"  • {date}: {value}")
        
        lines.append("")
        lines.append("💡 **Next Steps**")
        lines.append("Consider exploring:")
        lines.append("• Relationships between numeric columns using the correlation analysis")
        lines.append("• Distribution patterns in the histograms and box plots")
        lines.append("• Any outliers or unusual patterns in the data")
        lines.append("• Additional data sources to enrich your analysis")
        
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

    def _create_user_specific_tools(self):
        """Create tool wrappers that automatically include the user_id"""
        @traceable
        def analyze_data_file_wrapper(file_bytes: bytes) -> str:
            """Analyze an uploaded Excel or CSV file and generate comprehensive insights, visualizations, and statistics."""
            try:
                if not file_bytes or len(file_bytes) == 0:
                    return "❌ No file data provided. Please upload an Excel (.xlsx/.xls) or CSV file for analysis."
                
                result = self.analyze(file_bytes)
                
                # If there's an error in the analysis, return a user-friendly message
                if isinstance(result, dict) and "error" in result:
                    return f"❌ **Analysis Error**: {result['error']}\n\nPlease check that your file is a valid Excel or CSV file with data."
                
                # If successful, return the complete analysis with all components
                if isinstance(result, dict) and "summary" in result:
                    # Build comprehensive response with all analysis components
                    response_parts = []
                    
                    # 1. Summary
                    response_parts.append(f"📊 **COMPREHENSIVE DATA ANALYSIS COMPLETE!**\n")
                    response_parts.append(result['summary'])
                    
                    # 2. Descriptive Statistics
                    if "description" in result:
                        response_parts.append("\n📈 **DESCRIPTIVE STATISTICS**")
                        desc = result["description"]
                        for col, stats in desc.items():
                            if isinstance(stats, dict):
                                response_parts.append(f"\n**{col}**:")
                                for stat_name, stat_value in stats.items():
                                    if stat_value is not None and stat_name != 'count':
                                        if isinstance(stat_value, (int, float)):
                                            response_parts.append(f"  • {stat_name.title()}: {stat_value:.2f}")
                                        else:
                                            response_parts.append(f"  • {stat_name.title()}: {stat_value}")
                    
                    # 3. Forecast Information
                    if "forecast" in result and result["forecast"]:
                        response_parts.append("\n🔮 **FORECASTING RESULTS**")
                        if isinstance(result["forecast"], dict):
                            for date, value in result["forecast"].items():
                                if isinstance(value, (int, float)):
                                    response_parts.append(f"  • {date}: {value:.2f}")
                                else:
                                    response_parts.append(f"  • {date}: {value}")
                        else:
                            response_parts.append(f"  • {result['forecast']}")
                    
                    # 4. Visualizations Generated
                    if "plots" in result and result["plots"]:
                        plot_count = len(result["plots"])
                        response_parts.append(f"\n📊 **VISUALIZATIONS GENERATED**")
                        response_parts.append(f"Created {plot_count} visualizations including:")
                        
                        plot_types = []
                        for plot_name in result["plots"].keys():
                            if "hist" in plot_name:
                                plot_types.append("Histograms")
                            elif "box" in plot_name:
                                plot_types.append("Box Plots")
                            elif "scatter" in plot_name:
                                plot_types.append("Scatter Plots")
                            elif "correlation" in plot_name:
                                plot_types.append("Correlation Heatmap")
                            elif "forecast" in plot_name:
                                plot_types.append("Time Series Forecast")
                        
                        # Remove duplicates and list unique plot types
                        unique_plot_types = list(set(plot_types))
                        for plot_type in unique_plot_types:
                            response_parts.append(f"  • {plot_type}")
                    
                    # 5. Analysis Report ID
                    if "report_id" in result:
                        response_parts.append(f"\n🆔 **Report ID**: {result['report_id']}")
                    
                    return "\n".join(response_parts)
                
                return str(result)
                
            except Exception as e:
                return f"❌ **Unexpected Error**: {str(e)}\n\nPlease try uploading your file again or contact support if the issue persists."
        
        return [analyze_data_file_wrapper]

    def set_user_id(self, user_id: str):
        """Set the user ID for user-specific functionality"""
        self.user_id = user_id
        # Recreate tools with new user_id
        self.tools = self._create_user_specific_tools()
        # Recreate agent with new tools
        self.agent = create_react_agent(
            model=self.llm,
            tools=self.tools,
            prompt=self.persona,
            name="data_analyst_agent"
        )

    def get_agent(self):
        """Get the compiled agent for use in orchestration"""
        return self.agent

    def get_description(self):
        return "Analyzes uploaded Excel and CSV files and generates reports with plots, statistics, and forecasts."
    
    def get_name(self) -> str:
        """Get the agent's name for routing"""
        return "data_analyst_agent"
    
    def process(self, user_message: str, conversation_history: Optional[List[Dict]] = None, file_bytes: Optional[bytes] = None) -> str:
        """
        Process a user message and return a response.
        
        Args:
            user_message: The user's message
            conversation_history: Previous conversation messages for context
            file_bytes: Optional file bytes for data analysis
            
        Returns:
            The agent's response as a string
        """
        try:
            # Check if this is a data analysis request without a file
            analysis_keywords = [
                "analyze", "analysis", "data", "excel", "csv", "spreadsheet", 
                "chart", "graph", "statistics", "insights", "visualization",
                "correlation", "trend", "forecast", "summary"
            ]
            
            user_message_lower = user_message.lower()
            is_analysis_request = any(keyword in user_message_lower for keyword in analysis_keywords)
            
            # If it's an analysis request but no file is provided, give helpful guidance
            if is_analysis_request and file_bytes is None:
                return """📊 **Data Analysis Specialist at your service!**

I'd be happy to help you analyze your data! However, I need you to upload a data file first.

**What I can analyze:**
• Excel files (.xlsx, .xls)
• CSV files
• Statistical summaries and insights
• Data visualizations (histograms, box plots, scatter plots, correlations)
• Time series forecasting (when applicable)
• Pattern recognition and outlier detection

**To get started:**
1. Prepare your Excel or CSV file
2. Upload it when you make your request
3. I'll provide comprehensive analysis with insights and visualizations

**What makes for great analysis:**
• Clean, structured data
• Multiple columns for correlation analysis
• Date columns for time series forecasting
• Numeric data for statistical insights

Once you have your file ready, just upload it and ask me to analyze it! I'm here to help you uncover the stories hidden in your data. 🔍"""

            # Create messages for the agent
            messages = []
            
            # Add conversation history if provided
            if conversation_history:
                for msg in conversation_history:
                    if isinstance(msg.get("content"), str):
                        msg["content"] = [{"text": msg["content"]}]
                    elif isinstance(msg.get("content"), list):
                        msg["content"] = [c if isinstance(c, dict) else {"text": c} for c in msg["content"]]
                    messages.append(msg)
            
            # Add the current user input in correct schema
            messages.append({"role": "user", "content": [{"text": user_message}]})
            
            # If file is provided, add context about the file
            if file_bytes is not None:
                # Add a system message to inform the agent about the file
                messages.insert(0, {
                    "role": "system", 
                    "content": [{"text": "A data file has been uploaded and is available for analysis. Use the analyze_data_file tool to perform comprehensive analysis including descriptive statistics, visualizations, forecasts, and insights."}]
                })
            
            # Invoke the agent
            response = self.agent.invoke({"messages": messages})
            
            # Extract the response content
            if "messages" in response and response["messages"]:
                return response["messages"][-1].content
            else:
                return "I've processed your data analysis request. How else can I help you?"
                
        except Exception as e:
            return f"I encountered an error while processing your data analysis request: {str(e)}. Please try again." 