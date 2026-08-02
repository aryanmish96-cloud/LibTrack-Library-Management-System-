package com.libtrack.dto.item;

public class JournalCreateRequest extends ItemCreateRequest {
    private Integer issueNumber;
    private Integer volume;

    public Integer getIssueNumber() { return issueNumber; }
    public void setIssueNumber(Integer issueNumber) { this.issueNumber = issueNumber; }

    public Integer getVolume() { return volume; }
    public void setVolume(Integer volume) { this.volume = volume; }
}
