package com.uav.inspection.service.impl;

import com.uav.inspection.dao.InspectionTaskRepository;
import com.uav.inspection.entity.InspectionTask;
import com.uav.inspection.service.InspectionTaskService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Optional;

/**
 * 巡检任务业务逻辑实现
 */
@Service
public class InspectionTaskServiceImpl implements InspectionTaskService {

    @Autowired
    private InspectionTaskRepository taskRepository;

    @Override
    public List<InspectionTask> getAllTasks() {
        return taskRepository.findAll();
    }

    @Override
    public Page<InspectionTask> getTasksPage(Pageable pageable) {
        return taskRepository.findAll(pageable);
    }

    @Override
    public Optional<InspectionTask> getTaskById(Long id) {
        return taskRepository.findById(id);
    }

    @Override
    public InspectionTask createTask(InspectionTask task) {
        return taskRepository.save(task);
    }

    @Override
    public InspectionTask updateTask(InspectionTask task) {
        return taskRepository.save(task);
    }

    @Override
    public void deleteTask(Long id) {
        taskRepository.deleteById(id);
    }

    @Override
    public List<InspectionTask> getTasksByDeviceId(Long deviceId) {
        return taskRepository.findByDeviceId(deviceId);
    }

    @Override
    public List<InspectionTask> getTasksByStatus(String status) {
        return taskRepository.findByStatus(status);
    }
}
