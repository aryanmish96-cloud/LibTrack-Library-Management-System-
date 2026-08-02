package com.libtrack.dto.item;

public class EBookCreateRequest extends ItemCreateRequest {
    private String fileFormat = "PDF";
    private String downloadUrl;

    public String getFileFormat() { return fileFormat; }
    public void setFileFormat(String fileFormat) { this.fileFormat = fileFormat; }

    public String getDownloadUrl() { return downloadUrl; }
    public void setDownloadUrl(String downloadUrl) { this.downloadUrl = downloadUrl; }
}
