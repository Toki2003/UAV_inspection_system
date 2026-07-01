package com.uav.inspection.dao;

import com.uav.inspection.entity.InspectionTask;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

/**
 * 巡检任务数据访问通界
 */
@Repository
public interface InspectionTaskRepository extends JpaRepository<InspectionTask, Long> {

    /**
     * 根据设备ID查询任务
     */
    List<InspectionTask> findByDeviceId(Long deviceId);

    /**
     * 根据状态查询任务
     */
    List<InspectionTask> findByStatus(String status);

    /**
     * 根据区域ID查询任务
     */
    List<InspectionTask> findByAreaId(Long areaId);
}
