package com.uav.inspection.controller;

import com.uav.inspection.entity.Device;
import com.uav.inspection.service.DeviceService;
import com.uav.inspection.util.ApiResponse;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Optional;

/**
 * 设备管理控制器
 */
@RestController
@RequestMapping("/api/device")
@CrossOrigin(origins = "*", maxAge = 3600)
public class DeviceController {

    @Autowired
    private DeviceService deviceService;

    /**
     * 获取所有设备
     */
    @GetMapping("/list")
    public ApiResponse<List<Device>> getDeviceList() {
        try {
            List<Device> devices = deviceService.getAllDevices();
            return ApiResponse.success("获取设备列表成功", devices);
        } catch (Exception e) {
            return ApiResponse.fail("获取设备列表失败: " + e.getMessage());
        }
    }

    /**
     * 根据ID获取设备详情
     */
    @GetMapping("/{id}")
    public ApiResponse<Device> getDeviceDetail(@PathVariable Long id) {
        try {
            Optional<Device> device = deviceService.getDeviceById(id);
            if (device.isPresent()) {
                return ApiResponse.success("获取设备详情成功", device.get());
            }
            return ApiResponse.fail(404, "设备不存在");
        } catch (Exception e) {
            return ApiResponse.fail("获取设备详情失败: " + e.getMessage());
        }
    }

    /**
     * 根据设备代码获取
     */
    @GetMapping("/code/{code}")
    public ApiResponse<Device> getDeviceByCode(@PathVariable String code) {
        try {
            Optional<Device> device = deviceService.getDeviceByCode(code);
            if (device.isPresent()) {
                return ApiResponse.success("获取设备成功", device.get());
            }
            return ApiResponse.fail(404, "设备不存在");
        } catch (Exception e) {
            return ApiResponse.fail("获取设备失败: " + e.getMessage());
        }
    }

    /**
     * 创建设备
     */
    @PostMapping("/create")
    public ApiResponse<Device> createDevice(@RequestBody Device device) {
        try {
            Device newDevice = deviceService.createDevice(device);
            return ApiResponse.success("创建设备成功", newDevice);
        } catch (Exception e) {
            return ApiResponse.fail("创建设备失败: " + e.getMessage());
        }
    }

    /**
     * 更新设备
     */
    @PutMapping("/{id}")
    public ApiResponse<Device> updateDevice(
            @PathVariable Long id,
            @RequestBody Device device) {
        try {
            device.setId(id);
            Device updatedDevice = deviceService.updateDevice(device);
            return ApiResponse.success("更新设备成功", updatedDevice);
        } catch (Exception e) {
            return ApiResponse.fail("更新设备失败: " + e.getMessage());
        }
    }

    /**
     * 删除设备
     */
    @DeleteMapping("/{id}")
    public ApiResponse<String> deleteDevice(@PathVariable Long id) {
        try {
            deviceService.deleteDevice(id);
            return ApiResponse.success("删除设备成功", "");
        } catch (Exception e) {
            return ApiResponse.fail("删除设备失败: " + e.getMessage());
        }
    }

    /**
     * 获取在线设备列表
     */
    @GetMapping("/online")
    public ApiResponse<List<Device>> getOnlineDevices() {
        try {
            List<Device> devices = deviceService.getDevicesByStatus("在线");
            return ApiResponse.success("获取在线设备成功", devices);
        } catch (Exception e) {
            return ApiResponse.fail("获取在线设备失败: " + e.getMessage());
        }
    }

    /**
     * 获取在线设备数量
     */
    @GetMapping("/online/count")
    public ApiResponse<Long> getOnlineDeviceCount() {
        try {
            Long count = deviceService.getOnlineDeviceCount();
            return ApiResponse.success("获取在线设备数量成功", count);
        } catch (Exception e) {
            return ApiResponse.fail("获取在线设备数量失败: " + e.getMessage());
        }
    }
}
