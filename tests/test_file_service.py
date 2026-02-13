import pytest


@pytest.mark.asyncio
async def test_upload_file_success(file_service):
    result = await file_service.upload_file(b"fake image data", "photo.png", "uploads")
    assert "file_url" in result
    assert result["file_url"].startswith("https://storage.example.com/uploads/")
    assert result["file_name"].endswith(".png")
    assert result["file_size"] == len(b"fake image data")
    assert result["content_type"] == "image/png"


@pytest.mark.asyncio
async def test_upload_detects_mime_type_png(file_service):
    result = await file_service.upload_file(b"data", "image.png", "uploads")
    assert result["content_type"] == "image/png"


@pytest.mark.asyncio
async def test_upload_detects_mime_type_pdf(file_service):
    result = await file_service.upload_file(b"data", "document.pdf", "uploads")
    assert result["content_type"] == "application/pdf"


@pytest.mark.asyncio
async def test_upload_detects_mime_type_jpeg(file_service):
    result = await file_service.upload_file(b"data", "photo.jpeg", "uploads")
    assert result["content_type"] == "image/jpeg"


@pytest.mark.asyncio
async def test_upload_file_size_exceeds_limit(file_service):
    # Default limit is 10MB
    big_content = b"x" * (11 * 1024 * 1024)
    with pytest.raises(ValueError, match="size"):
        await file_service.upload_file(big_content, "big.png", "uploads")


@pytest.mark.asyncio
async def test_upload_file_type_not_allowed(file_service):
    with pytest.raises(ValueError, match="not allowed"):
        await file_service.upload_file(b"data", "malware.exe", "uploads")


@pytest.mark.asyncio
async def test_upload_no_extension(file_service):
    with pytest.raises(ValueError, match="not allowed"):
        await file_service.upload_file(b"data", "noextension", "uploads")


@pytest.mark.asyncio
async def test_delete_file_success(file_service, fake_storage):
    # Upload first
    await file_service.upload_file(b"data", "temp.png", "uploads")
    assert len(fake_storage.files) == 1

    # Delete
    result = await file_service.delete_file(list(fake_storage.files.keys())[0])
    assert result is True
    assert len(fake_storage.files) == 0


@pytest.mark.asyncio
async def test_get_presigned_url(file_service):
    url = await file_service.get_presigned_url("uploads/test.png")
    assert url == "https://storage.example.com/uploads/test.png"
