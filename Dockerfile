# Start with an official PyTorch image that includes CUDA for GPU support
FROM pytorch/pytorch:2.2.0-cuda12.1-cudnn8-runtime

# Install system packages (ffmpeg is crucial for your audio processing)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user (Required by Hugging Face Spaces)
RUN useradd -m -u 1000 user

# Set up the environment
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH \
    PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR $HOME/app

# Copy your requirements files first to leverage Docker cache
COPY --chown=user requirements_space.txt requirements_hf.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements_space.txt && \
    pip install --no-cache-dir -r requirements_hf.txt

# Copy the rest of your application code
COPY --chown=user . $HOME/app

# Switch to the non-root user
USER user

# Hugging Face Spaces expose port 7860 by default
EXPOSE 7860

# Command to run your app
CMD ["python", "server.py"]
