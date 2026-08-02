package com.libtrack.model;

import jakarta.persistence.*;

/**
 * Academic journal — joined table "journals" extending "items".
 * Maps to Python's Journal subclass.
 */
@Entity
@Table(name = "journals")
@DiscriminatorValue("journal")
public class Journal extends LibraryItem {

    @Column(name = "issue_number")
    private Integer issueNumber;

    private Integer volume;

    public Integer getIssueNumber() { return issueNumber; }
    public void setIssueNumber(Integer issueNumber) { this.issueNumber = issueNumber; }

    public Integer getVolume() { return volume; }
    public void setVolume(Integer volume) { this.volume = volume; }
}
