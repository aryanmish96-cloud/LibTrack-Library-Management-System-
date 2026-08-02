package com.libtrack.repository;

import com.libtrack.model.LibraryItem;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface ItemRepository extends JpaRepository<LibraryItem, Long> {

    @Query("SELECT i FROM LibraryItem i WHERE LOWER(i.title) LIKE LOWER(CONCAT('%', :query, '%'))")
    List<LibraryItem> searchByTitleContaining(@Param("query") String query);

    @Query("SELECT i FROM LibraryItem i WHERE LOWER(i.title) = LOWER(:title)")
    List<LibraryItem> findByTitleExact(@Param("title") String title);

    @Query("SELECT i FROM LibraryItem i WHERE LOWER(i.title) >= LOWER(:start) AND LOWER(i.title) <= LOWER(:end) ORDER BY LOWER(i.title)")
    List<LibraryItem> findByTitleRange(@Param("start") String start, @Param("end") String end);

    @Query("SELECT i FROM LibraryItem i ORDER BY LOWER(i.title)")
    List<LibraryItem> findAllAlphabetical();
}
