import request from './request';
export function getDroneTelemetry(deviceCode) {
  return request.get(
    `/drone-control/${deviceCode}/telemetry`
  )
}
export function getDroneVideo(
  deviceCode,
  streamType = 'uav'
) {
  return request.get(
    `/drone-control/${deviceCode}/video`,
    {
      params: {streamType}
    }
  )
}
export function sendDroneCommand(
  deviceCode,
  command
) {
  return request.post(
    `/drone-control/${deviceCode}/command`,
    {
      command
    }
  )
}
export function getDockOverview() {
  return request.get(
    '/drone-control/docks/overview'
  )
}
export function getDockList() {
  return request.get(
    '/drone-control/docks/list'
  )
}
export function getDroneSafety(deviceCode) {
  return request.get(
    `/drone-control/${deviceCode}/safety`
  )
}
export function getDroneAlertStatus(deviceCode) {
  return request.get(
    `/drone-control/${deviceCode}/alerts/status`
  )
}
export function requestDroneTakeover(deviceCode) {
  return request.post(
    `/drone-control/${deviceCode}/takeover`
  )
}
export function getDroneEmqxStatus(deviceCode) {
  return request.get(
    `/drone-control/${deviceCode}/emqx/status`
  )
}
export function subscribeDroneEmqx(deviceCode) {
  return request.post(
    `/drone-control/${deviceCode}/emqx/subscribe`
  )
}
