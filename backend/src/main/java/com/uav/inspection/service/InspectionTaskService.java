package com.uav.inspection.service;

import com.uav.inspection.entity.InspectionTask;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;

import java.util.List;
import java.util.Optional;

/**
 * 巡检任务业务逻辑接口
 */
public interface InspectionTaskService {

    /**
     * 获取所有任务
     */
    List<InspectionTask> getAllTasks();

    /**
     * 分页获取任务
     */
    Page<InspectionTask> getTasksPage(Pageable pageable);

    /**
     * 根据ID获取任务
     */
    Optional<InspectionTask> getTaskById(Long id);

    /**
     * 创建任务
     */
    InspectionTask createTask(InspectionTask task);

    /**
     * 更新任务
     */
    InspectionTask updateTask(InspectionTask task);

    /**
     * 删除任务
     */
    void deleteTask(Long id);

    /**
     * 根据设备ID查询任务
     */
    List<InspectionTask> getTasksByDeviceId(Long deviceId);

    /**
     * 根据状态查询任务
     */
    List<InspectionTask> getTasksByStatus(String status);
}
