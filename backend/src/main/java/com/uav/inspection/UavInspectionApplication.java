package com.uav.inspection;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cache.annotation.EnableCaching;

/**
 * UAV 无人机巡检系统主启动类
 */
@SpringBootApplication
@EnableCaching
public class UavInspectionApplication {

    public static void main(String[] args) {
        SpringApplication.run(UavInspectionApplication.class, args);
    }
}
