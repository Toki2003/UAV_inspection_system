import request from './request';
export function getDroneTelemetry(deviceCode) {
  return request.get(
    `/drone-control/${deviceCode}/telemetry`
  )
}
export function getDroneVideo(deviceCode) {
  return request.get(
    `/drone-control/${deviceCode}/video`
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