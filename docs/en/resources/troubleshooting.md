# Troubleshooting

Common issues and solutions for Hyper-Extract.

## Installation Issues

### Package Installation Fails

**Problem**: `pip install hyper-extract` fails

**Solutions**:
1. Upgrade pip:
   ```bash
   pip install --upgrade pip
   ```

2. Use a virtual environment:
   ```bash
   python -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   pip install hyper-extract
   ```

### Dependency Conflicts

**Problem**: Dependency conflicts with other packages

**Solution**: Create a clean virtual environment:
```bash
python -m venv hyper-extract-env
source hyper-extract-env/bin/activate
pip install hyper-extract
```

## API Issues

### Invalid API Key

**Problem**: "Invalid API key" error

**Solutions**:
1. Verify your API key is correct
2. Check key has not expired
3. Ensure sufficient credits/quota

### Rate Limiting

**Problem**: "Rate limit exceeded" error

**Solutions**:
1. Add delay between requests
2. Use batch processing
3. Reduce `max_workers` in configuration

### Timeout Errors

**Problem**: Requests timeout

**Solutions**:
1. Increase timeout in configuration:
   ```yaml
   extraction:
     timeout: 120
   ```
2. Use smaller document chunks
3. Check network connectivity

## Extraction Issues

### Empty Results

**Problem**: Extraction returns no results

**Solutions**:
1. Verify document contains extractable content
2. Check template matches document type
3. Review extraction logs for errors

### Incorrect Extractions

**Problem**: Extracted data is incorrect or incomplete

**Solutions**:
1. Use more specific templates
2. Add extraction hints in template description
3. Try different extraction methods
4. Adjust confidence thresholds

### Memory Issues

**Problem**: Out of memory errors

**Solutions**:
1. Process documents in smaller batches
2. Reduce batch size
3. Clear cache periodically

## Performance Issues

### Slow Extraction

**Problem**: Extraction is very slow

**Solutions**:
1. Use faster extraction methods:
   ```python
   result = atom.extract(text)  # Fastest
   ```

2. Enable parallel processing:
   ```python
   results = ka.batch_parse(docs, parallel=True)
   ```

3. Use lighter models for faster processing

## CLI Issues

### Command Not Found

**Problem**: `he` command not found

**Solutions**:
1. Reinstall the package:
   ```bash
   pip uninstall hyper-extract
   pip install hyper-extract
   ```

2. Use Python module directly:
   ```bash
   python -m hyperextract parse document.txt
   ```

### Configuration Not Found

**Problem**: CLI can't find configuration

**Solution**: Initialize configuration:
```bash
he config init -k YOUR_API_KEY
```

## Still Having Issues?

If you're still experiencing issues:
1. Check the [FAQ](faq.md)
2. Search existing [GitHub Issues](https://github.com/hyper-extract/hyper-extract/issues)
3. Create a new issue with detailed information
