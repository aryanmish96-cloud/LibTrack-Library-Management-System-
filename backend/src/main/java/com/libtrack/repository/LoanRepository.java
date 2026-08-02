package com.libtrack.repository;

import com.libtrack.model.Loan;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.Instant;
import java.util.List;
import java.util.Optional;

@Repository
public interface LoanRepository extends JpaRepository<Loan, Long> {

    List<Loan> findByMemberIdOrderByCheckoutDateDesc(Long memberId);

    @Query("SELECT l FROM Loan l WHERE l.returnDate IS NULL AND l.dueDate < :now")
    List<Loan> findOverdue(@Param("now") Instant now);

    @Query("SELECT l FROM Loan l WHERE l.item.id = :itemId AND l.member.id = :memberId AND l.returnDate IS NULL")
    Optional<Loan> findActiveByItemAndMember(@Param("itemId") Long itemId, @Param("memberId") Long memberId);
}
