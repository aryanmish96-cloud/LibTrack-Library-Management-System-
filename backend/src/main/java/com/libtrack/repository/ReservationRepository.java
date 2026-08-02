package com.libtrack.repository;

import com.libtrack.model.Reservation;
import com.libtrack.model.ReservationStatus;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface ReservationRepository extends JpaRepository<Reservation, Long> {

    List<Reservation> findByMemberIdOrderByReservationDateDesc(Long memberId);

    long countByItemIdAndStatus(Long itemId, ReservationStatus status);

    @Query("SELECT r FROM Reservation r WHERE r.item.id = :itemId AND r.status = :status ORDER BY r.queuePosition ASC")
    List<Reservation> findByItemIdAndStatusOrderByPosition(@Param("itemId") Long itemId, @Param("status") ReservationStatus status);

    @Query("SELECT r FROM Reservation r WHERE r.item.id = :itemId AND r.member.id = :memberId AND r.status IN ('WAITING','READY')")
    Optional<Reservation> findActiveByItemAndMember(@Param("itemId") Long itemId, @Param("memberId") Long memberId);
}
