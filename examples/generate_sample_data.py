"""Generate sample datasets for testing and benchmarking."""

import random
from pathlib import Path

import polars as pl


def generate_text_dataset(n_rows: int = 10000, duplicate_ratio: float = 0.15) -> pl.DataFrame:
    """Generate a text dataset with some duplicates."""
    topics = [
        "machine learning", "deep learning", "neural networks", "artificial intelligence",
        "data science", "natural language processing", "computer vision", "reinforcement learning",
        "supervised learning", "unsupervised learning", "transfer learning", "model training"
    ]
    
    templates = [
        "Introduction to {topic} and its applications",
        "Advanced techniques in {topic} for beginners",
        "Understanding {topic} with practical examples",
        "A comprehensive guide to {topic}",
        "Best practices for {topic} in production",
        "How to implement {topic} efficiently",
        "The future of {topic} in AI research",
        "Common challenges in {topic} and solutions"
    ]
    
    data = []
    unique_rows = int(n_rows * (1 - duplicate_ratio))
    
    # Generate unique rows
    for i in range(unique_rows):
        topic = random.choice(topics)
        template = random.choice(templates)
        text = template.format(topic=topic)
        
        data.append({
            "id": i,
            "text": text,
            "category": topic.split()[0],
            "length": len(text),
            "quality": random.uniform(0.5, 1.0)
        })
    
    # Add duplicates
    duplicate_count = n_rows - unique_rows
    for _ in range(duplicate_count):
        data.append(random.choice(data).copy())
    
    # Shuffle
    random.shuffle(data)
    
    return pl.DataFrame(data)


def generate_instruction_dataset(n_rows: int = 5000) -> pl.DataFrame:
    """Generate an instruction-following dataset."""
    instructions = [
        "Write a function to calculate fibonacci numbers",
        "Explain the concept of recursion",
        "Create a REST API endpoint for user authentication",
        "Implement a binary search algorithm",
        "Design a database schema for an e-commerce platform",
        "Write unit tests for a sorting function",
        "Optimize a SQL query for better performance",
        "Implement a caching mechanism using Redis"
    ]
    
    responses = [
        "Here's a detailed implementation...",
        "Let me explain this concept step by step...",
        "I'll show you how to build this...",
        "The solution involves the following steps...",
        "Here's an efficient approach...",
        "Let's break this down...",
        "I recommend the following design...",
        "Here's how you can implement this..."
    ]
    
    data = []
    for i in range(n_rows):
        instruction = random.choice(instructions)
        response = random.choice(responses) + " " + instruction.lower()
        
        data.append({
            "id": i,
            "instruction": instruction,
            "response": response,
            "category": "coding" if "function" in instruction or "implement" in instruction else "explanation",
            "quality_score": random.uniform(0.3, 1.0)
        })
    
    return pl.DataFrame(data)


def generate_mixed_dataset(n_rows: int = 8000) -> pl.DataFrame:
    """Generate a mixed dataset with various data types."""
    categories = ["A", "B", "C", "D", "E"]
    
    data = []
    for i in range(n_rows):
        data.append({
            "id": i,
            "name": f"item_{i % 1000}",  # Creates some duplicates
            "category": random.choice(categories),
            "value": random.uniform(0, 100),
            "count": random.randint(1, 1000),
            "description": f"This is item number {i} in category {random.choice(categories)}",
            "is_active": random.choice([True, False]),
            "rating": random.uniform(1.0, 5.0)
        })
    
    return pl.DataFrame(data)


def main():
    """Generate all sample datasets."""
    output_dir = Path("examples/data")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("Generating sample datasets...")
    
    # Text dataset
    print("  - text_dataset.csv (10k rows)")
    text_df = generate_text_dataset(10000)
    text_df.write_csv(output_dir / "text_dataset.csv")
    
    # Instruction dataset
    print("  - instruction_dataset.csv (5k rows)")
    instruction_df = generate_instruction_dataset(5000)
    instruction_df.write_csv(output_dir / "instruction_dataset.csv")
    
    # Mixed dataset
    print("  - mixed_dataset.csv (8k rows)")
    mixed_df = generate_mixed_dataset(8000)
    mixed_df.write_csv(output_dir / "mixed_dataset.csv")
    
    # Small test dataset
    print("  - small_test.csv (100 rows)")
    small_df = generate_text_dataset(100, duplicate_ratio=0.2)
    small_df.write_csv(output_dir / "small_test.csv")
    
    print("\nDatasets generated successfully!")
    print(f"Output directory: {output_dir.absolute()}")


if __name__ == "__main__":
    main()
