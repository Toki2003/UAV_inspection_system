package com.uav.inspection.service.impl;

import com.uav.inspection.dao.DeviceRepository;
import com.uav.inspection.entity.Device;
import com.uav.inspection.service.DeviceService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Optional;

/**
 * 设备业务逻辑实现
 */
@Service
public class DeviceServiceImpl implements DeviceService {

    @Autowired
    private DeviceRepository deviceRepository;

    @Override
    public List<Device> getAllDevices() {
        return deviceRepository.findAll();
    }

    @Override
    public Optional<Device> getDeviceById(Long id) {
        return deviceRepository.findById(id);
    }

    @Override
    public Optional<Device> getDeviceByCode(String code) {
        return deviceRepository.findByCode(code);
    }

    @Override
    public Device createDevice(Device device) {
        return deviceRepository.save(device);
    }

    @Override
    public Device updateDevice(Device device) {
        return deviceRepository.save(device);
    }

    @Override
    public void deleteDevice(Long id) {
        deviceRepository.deleteById(id);
    }

    @Override
    public List<Device> getDevicesByStatus(String status) {
        return deviceRepository.findByStatus(status);
    }

    @Override
    public Long getOnlineDeviceCount() {
        return deviceRepository.findByStatus("在线").stream().count();
    }
}
