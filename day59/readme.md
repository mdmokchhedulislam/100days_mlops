The xFusionCorp Industries ML platform team processes the overnight batch of transactions using a fraud-detection model. This process is executed with a standalone script that reads from input.csv, applies the pre-trained RandomForest model to each row, and generates predictions.csv. A scaffold for the script, located at /root/code/serving/batch_predict.py, includes the paths for the model, input, and output; however, the scoring flow is currently marked as TODO.

Your objective is to implement the batch scoring process within the script. Specifically, you need to ensure that it reads input.csv, utilizes the pre-trained model to score each row, and outputs predictions.csv, which should include a column for integer prediction class labels. After implementing the flow, run the script.


The project layout under /root/code/serving/:

model.pkl – Deterministic RandomForest trained at startup on the shared amount / hour / num_tx_past_day → is_fraud synthetic dataset.
input.csv – The 10-row batch input: three feature columns, no label column.
batch_predict.py – The scorer scaffold. The MODEL_PATH / INPUT_CSV / OUTPUT_CSV constants are set; the scoring flow (load the model, read the input, add an integer prediction column via model.predict(...), write the output) is left as a TODO to author.
The end state must include:

/root/code/serving/predictions.csv exists.
The output carries the three input columns plus a prediction column.
Every value in prediction is 0 or 1 (integer class label), not a float probability.
The output row count matches the input row count.