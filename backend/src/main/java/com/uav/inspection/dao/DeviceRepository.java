package com.uav.inspection.dao;

import com.uav.inspection.entity.Device;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

/**
 * 设备数据访问层
 */
@Repository
public interface DeviceRepository extends JpaRepository<Device, Long> {

    /**
     * 根据设备代码查询
     */
    Optional<Device> findByCode(String code);

    /**
     * 根据状态查询
     */
    List<Device> findByStatus(String status);

    /**
     * 根据类型查询
     */
    List<Device> findByType(String type);
}
