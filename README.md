E-Commerce Customer Segmentation using Apache Spark & Streamlit
1. Overview

This project focuses on customer segmentation using RFM (Recency, Frequency, Monetary) analysis with Apache Spark for distributed data processing and Streamlit for interactive visualization.
It applies K-Means clustering to group customers based on purchasing behavior, helping businesses tailor marketing strategies and improve customer retention.

2. Problem Statement

E-commerce platforms often deal with large-scale customer data. Understanding customer behavior is essential for retention, loyalty, and sales optimization.
The main goal of this project is to identify and segment customers based on how recently and frequently they purchase and how much they spend, providing actionable insights through data-driven clustering.

3. Objectives

Perform RFM analysis on customer data using PySpark.

Implement K-Means clustering to segment customers.

Visualize clusters using an interactive dashboard built with Streamlit.

Monitor Spark job execution through the Spark Web UI.

4. Technologies Used

Apache Spark (PySpark, Spark Shell) – for scalable data processing and clustering.

Streamlit – for interactive dashboard visualization.

Python (pandas, plotly.express) – for data manipulation and visualization.

Scala – for executing Spark shell commands and transformations.

Hadoop (winutils) – for Windows-based Spark operations.

Git & GitHub – for version control and collaboration.

5. Workflow / Implementation Steps
Step 1: Data Preprocessing

Load dataset (data.csv) into Spark using PySpark or Spark Shell.

Perform data cleaning and transformation.

Calculate RFM metrics:

Recency: Days since last purchase.

Frequency: Number of purchases made.

Monetary: Total amount spent by the customer.

Step 2: Feature Engineering and Clustering

Assemble the features into a vector using VectorAssembler.

Standardize data using StandardScaler.

Apply K-Means Clustering to group customers into clusters.

Store the clustered output as clustered_output.csv.

Step 3: Visualization Dashboard (Streamlit)

Load the clustered dataset into the dashboard.

Display data summary and key metrics.

Show interactive visualizations:

Cluster distribution (Pie chart)

Average RFM values per cluster (Bar chart)

3D visualization of clusters in RFM space.

Allow users to filter customers by cluster and download filtered data.

Step 4: Spark Web UI Monitoring

Launch Spark Web UI at http://localhost:4040 to monitor job stages, tasks, and memory usage.

6. Execution Steps
Run the PySpark Pipeline
spark-submit pyspark_pipeline.py data.csv clustered_output 4

Run the Streamlit Dashboard
streamlit run app.py

Access Spark Web UI

Open your browser and visit:

http://localhost:4040

7. Folder Structure
EcommerceSegmentation/

│

├── data.csv

├── pyspark_pipeline.py

├── app.py

├── clustered_output/

   └── clustered_output.csv


9. Results and Output

The output file clustered_output.csv contains segmented customer data with assigned cluster labels.

The Streamlit dashboard displays interactive graphs for better understanding of cluster behavior.

The Spark Web UI provides execution insights for performance analysis.

9. Future Enhancements

Integrate DB connectivity for dynamic data loading.

Deploy the dashboard as a web application.

Experiment with other clustering algorithms such as DBSCAN or hierarchical clustering.

Implement customer churn prediction using Spark MLlib.

10. Conclusion

This project demonstrates how big data tools like Apache Spark can efficiently handle customer segmentation tasks.
By combining RFM analysis, K-Means clustering, and Streamlit visualization, businesses can make informed decisions, enhance marketing strategies, and strengthen customer engagement.

11. Project Images

   <img width="1690" height="353" alt="Screenshot 2025-11-04 112804" src="https://github.com/user-attachments/assets/4f79a24e-8777-405b-96d3-b39e3fcb07da" />

   <img width="1811" height="859" alt="Screenshot 2025-11-04 112136" src="https://github.com/user-attachments/assets/95d53827-66ff-43cb-b5ef-7a86f8704e7d" />
   <img width="1805" height="687" alt="Screenshot 2025-11-04 112304" src="https://github.com/user-attachments/assets/2178b439-c70e-43f3-92ed-6938659afe22" />
   <img width="1779" height="751" alt="Screenshot 2025-11-04 112352" src="https://github.com/user-attachments/assets/85c4a209-fc0a-455a-bfe1-ec21f9c5495d" />
   <img width="1765" height="559" alt="Screenshot 2025-11-04 112435" src="https://github.com/user-attachments/assets/7b3d7998-121c-466c-a4b8-9cddc124bafb" />
   <img width="1715" height="637" alt="Screenshot 2025-11-04 112603" src="https://github.com/user-attachments/assets/93dc6d4f-e090-4476-81b5-a265be4a5e8f" />
   <img width="388" height="154" alt="Screenshot 2025-11-04 112630" src="https://github.com/user-attachments/assets/5db1dcf8-4366-4273-a0f7-80ff8b5fc57f" />





   


