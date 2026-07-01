package com.uav.inspection.service;

import com.uav.inspection.entity.Device;

import java.util.List;
import java.util.Optional;

/**
 * 设备业务逻辑接口
 */
public interface DeviceService {

    /**
     * 获取所有设备
     */
    List<Device> getAllDevices();

    /**
     * 根据ID获取设备
     */
    Optional<Device> getDeviceById(Long id);

    /**
     * 根据设备代码获取
     */
    Optional<Device> getDeviceByCode(String code);

    /**
     * 创建设备
     */
    Device createDevice(Device device);

    /**
     * 更新设备
     */
    Device updateDevice(Device device);

    /**
     * 删除设备
     */
    void deleteDevice(Long id);

    /**
     * 根据状态查询设备
     */
    List<Device> getDevicesByStatus(String status);

    /**
     * 获取在线设备数量
     */
    Long getOnlineDeviceCount();
}
