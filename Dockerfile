# Use the official AWS Lambda base image for Python 3.10
FROM public.ecr.aws/lambda/python:3.10

# Copy the function code and requirements.txt
COPY . ${LAMBDA_TASK_ROOT}
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

# Set the CMD to your handler
CMD ["app.handler"]
