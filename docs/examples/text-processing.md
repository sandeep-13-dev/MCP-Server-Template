# 📝 Text Processing Example

Comprehensive text processing tools demonstrating string manipulation, analysis, and transformation capabilities.

## Overview

This example implements various text processing operations as MCP tools:
- Text analysis (word count, character frequency)
- String transformations (case conversion, formatting)
- Text search and manipulation
- Content generation and templates

## Implementation

```python
# src/tools/text_processing_tools.py
from fastmcp import FastMCP
from typing import Dict, Any, List, Optional
import re
from collections import Counter
from .base import ToolError, format_success_response

mcp = FastMCP("Text Processing Server")

@mcp.tool
async def analyze_text(
    text: str,
    include_frequency: bool = True,
    include_readability: bool = False
) -> Dict[str, Any]:
    """
    Analyze text and provide statistics.
    
    Args:
        text: Text to analyze
        include_frequency: Include character/word frequency analysis
        include_readability: Include readability metrics
        
    Returns:
        Dict containing text analysis results
    """
    if not text.strip():
        raise ToolError("Text cannot be empty", "EMPTY_TEXT")
    
    # Basic statistics
    words = text.split()
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    analysis = {
        "character_count": len(text),
        "character_count_no_spaces": len(text.replace(" ", "")),
        "word_count": len(words),
        "sentence_count": len(sentences),
        "paragraph_count": len([p for p in text.split('\n\n') if p.strip()]),
        "average_words_per_sentence": round(len(words) / max(len(sentences), 1), 2),
        "average_characters_per_word": round(sum(len(word) for word in words) / max(len(words), 1), 2)
    }
    
    # Frequency analysis
    if include_frequency:
        char_freq = Counter(text.lower())
        word_freq = Counter(word.lower().strip('.,!?;:"()[]') for word in words)
        
        analysis["character_frequency"] = dict(char_freq.most_common(10))
        analysis["word_frequency"] = dict(word_freq.most_common(10))
    
    # Readability metrics (simplified)
    if include_readability:
        avg_sentence_length = len(words) / max(len(sentences), 1)
        # Simplified Flesch Reading Ease approximation
        reading_ease = 206.835 - (1.015 * avg_sentence_length)
        analysis["readability"] = {
            "average_sentence_length": round(avg_sentence_length, 2),
            "reading_ease_score": round(reading_ease, 2),
            "reading_level": "Easy" if reading_ease > 90 else "Moderate" if reading_ease > 60 else "Difficult"
        }
    
    return format_success_response(
        data=analysis,
        message="Text analysis completed successfully"
    )

@mcp.tool
async def transform_text(
    text: str,
    operation: str,
    custom_params: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Transform text using various operations.
    
    Args:
        text: Text to transform
        operation: Transformation type (uppercase, lowercase, title, reverse, etc.)
        custom_params: Additional parameters for specific operations
        
    Returns:
        Dict containing transformed text
    """
    if not text:
        raise ToolError("Text cannot be empty", "EMPTY_TEXT")
    
    params = custom_params or {}
    
    operations = {
        "uppercase": lambda t: t.upper(),
        "lowercase": lambda t: t.lower(),
        "title": lambda t: t.title(),
        "capitalize": lambda t: t.capitalize(),
        "reverse": lambda t: t[::-1],
        "remove_spaces": lambda t: t.replace(" ", ""),
        "remove_punctuation": lambda t: re.sub(r'[^\w\s]', '', t),
        "slugify": lambda t: re.sub(r'\W+', '-', t.lower()).strip('-'),
        "count_words": lambda t: str(len(t.split())),
        "extract_emails": lambda t: ' '.join(re.findall(r'\S+@\S+\.\S+', t)),
        "extract_urls": lambda t: ' '.join(re.findall(r'http[s]?://\S+', t))
    }
    
    if operation not in operations:
        raise ToolError(
            f"Unknown operation: {operation}. Available: {list(operations.keys())}", 
            "UNKNOWN_OPERATION"
        )
    
    try:
        transformed = operations[operation](text)
        
        return format_success_response(
            data={
                "original_text": text,
                "transformed_text": transformed,
                "operation": operation,
                "length_change": len(transformed) - len(text)
            },
            message=f"Text transformed using '{operation}' operation"
        )
    except Exception as e:
        raise ToolError(f"Transformation failed: {str(e)}", "TRANSFORMATION_ERROR")

@mcp.tool
async def find_and_replace(
    text: str,
    find: str,
    replace: str,
    case_sensitive: bool = True,
    use_regex: bool = False
) -> Dict[str, Any]:
    """
    Find and replace text patterns.
    
    Args:
        text: Source text
        find: Text or pattern to find
        replace: Replacement text
        case_sensitive: Whether search is case sensitive
        use_regex: Whether to use regex patterns
        
    Returns:
        Dict containing results of find and replace operation
    """
    if not text:
        raise ToolError("Text cannot be empty", "EMPTY_TEXT")
    
    if not find:
        raise ToolError("Find pattern cannot be empty", "EMPTY_FIND_PATTERN")
    
    try:
        original_text = text
        
        if use_regex:
            flags = 0 if case_sensitive else re.IGNORECASE
            result_text = re.sub(find, replace, text, flags=flags)
            matches = len(re.findall(find, text, flags=flags))
        else:
            if not case_sensitive:
                # Case insensitive replacement
                pattern = re.escape(find)
                result_text = re.sub(pattern, replace, text, flags=re.IGNORECASE)
                matches = len(re.findall(pattern, text, flags=re.IGNORECASE))
            else:
                result_text = text.replace(find, replace)
                matches = text.count(find)
        
        return format_success_response(
            data={
                "original_text": original_text,
                "result_text": result_text,
                "find_pattern": find,
                "replacement": replace,
                "matches_found": matches,
                "case_sensitive": case_sensitive,
                "used_regex": use_regex
            },
            message=f"Found and replaced {matches} occurrences"
        )
        
    except re.error as e:
        raise ToolError(f"Invalid regex pattern: {str(e)}", "INVALID_REGEX")
    except Exception as e:
        raise ToolError(f"Find and replace failed: {str(e)}", "REPLACEMENT_ERROR")

@mcp.tool
async def generate_lorem_ipsum(
    paragraphs: int = 1,
    words_per_paragraph: int = 50,
    start_with_lorem: bool = True
) -> Dict[str, Any]:
    """
    Generate Lorem Ipsum placeholder text.
    
    Args:
        paragraphs: Number of paragraphs to generate
        words_per_paragraph: Words per paragraph
        start_with_lorem: Whether to start with classic "Lorem ipsum..."
        
    Returns:
        Dict containing generated Lorem Ipsum text
    """
    if paragraphs < 1 or paragraphs > 100:
        raise ToolError("Paragraphs must be between 1 and 100", "INVALID_PARAGRAPH_COUNT")
    
    if words_per_paragraph < 1 or words_per_paragraph > 500:
        raise ToolError("Words per paragraph must be between 1 and 500", "INVALID_WORD_COUNT")
    
    lorem_words = [
        "lorem", "ipsum", "dolor", "sit", "amet", "consectetur", "adipiscing", "elit",
        "sed", "do", "eiusmod", "tempor", "incididunt", "ut", "labore", "et", "dolore",
        "magna", "aliqua", "enim", "ad", "minim", "veniam", "quis", "nostrud",
        "exercitation", "ullamco", "laboris", "nisi", "aliquip", "ex", "ea", "commodo",
        "consequat", "duis", "aute", "irure", "in", "reprehenderit", "voluptate",
        "velit", "esse", "cillum", "fugiat", "nulla", "pariatur", "excepteur", "sint",
        "occaecat", "cupidatat", "non", "proident", "sunt", "culpa", "qui", "officia",
        "deserunt", "mollit", "anim", "id", "est", "laborum"
    ]
    
    import random
    
    paragraphs_text = []
    
    for i in range(paragraphs):
        if i == 0 and start_with_lorem:
            # Start with classic Lorem ipsum
            words = ["Lorem", "ipsum", "dolor", "sit", "amet"]
            remaining_words = words_per_paragraph - 5
        else:
            words = []
            remaining_words = words_per_paragraph
        
        # Add random words
        for _ in range(remaining_words):
            words.append(random.choice(lorem_words))
        
        # Capitalize first word and add period
        if words:
            words[0] = words[0].capitalize()
            paragraph_text = " ".join(words) + "."
            paragraphs_text.append(paragraph_text)
    
    full_text = "\n\n".join(paragraphs_text)
    
    return format_success_response(
        data={
            "text": full_text,
            "paragraphs": paragraphs,
            "words_per_paragraph": words_per_paragraph,
            "total_words": sum(len(p.split()) for p in paragraphs_text),
            "total_characters": len(full_text)
        },
        message=f"Generated {paragraphs} paragraphs of Lorem Ipsum text"
    )
```

## Usage Examples

```python
# test_text_processing.py
import asyncio
import json
from fastmcp import Client

async def test_text_processing():
    client = Client("http://localhost:8000/mcp")
    
    async with client:
        # Text analysis
        text = "Hello world! This is a sample text for analysis. How are you today?"
        result = await client.call_tool("analyze_text", {
            "text": text,
            "include_frequency": True,
            "include_readability": True
        })
        analysis = json.loads(result[0].text)
        print(f"Word count: {analysis['data']['word_count']}")
        print(f"Reading level: {analysis['data']['readability']['reading_level']}")
        
        # Text transformation
        result = await client.call_tool("transform_text", {
            "text": "Hello World",
            "operation": "slugify"
        })
        transformed = json.loads(result[0].text)
        print(f"Slugified: {transformed['data']['transformed_text']}")
        
        # Find and replace
        result = await client.call_tool("find_and_replace", {
            "text": "The quick brown fox jumps over the lazy dog",
            "find": "the",
            "replace": "a",
            "case_sensitive": False
        })
        replaced = json.loads(result[0].text)
        print(f"Replaced text: {replaced['data']['result_text']}")
        
        # Generate Lorem Ipsum
        result = await client.call_tool("generate_lorem_ipsum", {
            "paragraphs": 2,
            "words_per_paragraph": 30
        })
        lorem = json.loads(result[0].text)
        print(f"Lorem Ipsum:\n{lorem['data']['text']}")

if __name__ == "__main__":
    asyncio.run(test_text_processing())
```

## Setup Instructions

1. Add the text processing tools to your project
2. Update `src/tools/__init__.py` to include `"tools.text_processing_tools"`
3. Start the server: `python src/server.py`
4. Test the tools: `python test_text_processing.py`

## Key Features

- **Comprehensive Analysis**: Word count, character frequency, readability metrics
- **Flexible Transformations**: Multiple text transformation operations
- **Pattern Matching**: Regex and simple find/replace functionality
- **Content Generation**: Lorem Ipsum placeholder text generation
- **Error Handling**: Robust validation and error reporting

This example demonstrates advanced string manipulation and analysis capabilities for MCP applications. 