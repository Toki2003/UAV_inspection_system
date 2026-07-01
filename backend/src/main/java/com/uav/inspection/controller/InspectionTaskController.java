package com.uav.inspection.controller;

import com.uav.inspection.entity.InspectionTask;
import com.uav.inspection.service.InspectionTaskService;
import com.uav.inspection.util.ApiResponse;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.PageRequest;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Optional;

/**
 * 巡检任务控制器
 */
@RestController
@RequestMapping("/api/inspection")
@CrossOrigin(origins = "*", maxAge = 3600)
public class InspectionTaskController {

    @Autowired
    private InspectionTaskService taskService;

    /**
     * 获取所有任务列表
     */
    @GetMapping("/list")
    public ApiResponse<List<InspectionTask>> getTaskList(
            @RequestParam(value = "page", defaultValue = "0") int page,
            @RequestParam(value = "size", defaultValue = "10") int size) {
        try {
            List<InspectionTask> tasks = taskService.getAllTasks();
            return ApiResponse.success("获取任务列表成功", tasks);
        } catch (Exception e) {
            return ApiResponse.fail("获取任务列表失败: " + e.getMessage());
        }
    }

    /**
     * 获取任务详情
     */
    @GetMapping("/{id}")
    public ApiResponse<InspectionTask> getTaskDetail(@PathVariable Long id) {
        try {
            Optional<InspectionTask> task = taskService.getTaskById(id);
            if (task.isPresent()) {
                return ApiResponse.success("获取任务详情成功", task.get());
            }
            return ApiResponse.fail(404, "任务不存在");
        } catch (Exception e) {
            return ApiResponse.fail("获取任务详情失败: " + e.getMessage());
        }
    }

    /**
     * 创建任务
     */
    @PostMapping("/create")
    public ApiResponse<InspectionTask> createTask(@RequestBody InspectionTask task) {
        try {
            InspectionTask newTask = taskService.createTask(task);
            return ApiResponse.success("创建任务成功", newTask);
        } catch (Exception e) {
            return ApiResponse.fail("创建任务失败: " + e.getMessage());
        }
    }

    /**
     * 更新任务
     */
    @PutMapping("/{id}")
    public ApiResponse<InspectionTask> updateTask(
            @PathVariable Long id,
            @RequestBody InspectionTask task) {
        try {
            task.setId(id);
            InspectionTask updatedTask = taskService.updateTask(task);
            return ApiResponse.success("更新任务成功", updatedTask);
        } catch (Exception e) {
            return ApiResponse.fail("更新任务失败: " + e.getMessage());
        }
    }

    /**
     * 删除任务
     */
    @DeleteMapping("/{id}")
    public ApiResponse<String> deleteTask(@PathVariable Long id) {
        try {
            taskService.deleteTask(id);
            return ApiResponse.success("删除任务成功", "");
        } catch (Exception e) {
            return ApiResponse.fail("删除任务失败: " + e.getMessage());
        }
    }

    /**
     * 根据设备ID获取任务
     */
    @GetMapping("/device/{deviceId}")
    public ApiResponse<List<InspectionTask>> getTasksByDevice(@PathVariable Long deviceId) {
        try {
            List<InspectionTask> tasks = taskService.getTasksByDeviceId(deviceId);
            return ApiResponse.success("获取设备任务成功", tasks);
        } catch (Exception e) {
            return ApiResponse.fail("获取设备任务失败: " + e.getMessage());
        }
    }

    /**
     * 根据状态获取任务
     */
    @GetMapping("/status/{status}")
    public ApiResponse<List<InspectionTask>> getTasksByStatus(@PathVariable String status) {
        try {
            List<InspectionTask> tasks = taskService.getTasksByStatus(status);
            return ApiResponse.success("获取任务成功", tasks);
        } catch (Exception e) {
            return ApiResponse.fail("获取任务失败: " + e.getMessage());
        }
    }
}
