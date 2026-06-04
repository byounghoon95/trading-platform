{{- define "marketpulse.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "marketpulse.fullname" -}}
{{- if .Values.fullnameOverride -}}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- include "marketpulse.name" . -}}
{{- end -}}
{{- end -}}

{{- define "marketpulse.namespace" -}}
{{- default .Release.Namespace .Values.namespace.name -}}
{{- end -}}

{{- define "marketpulse.labels" -}}
app.kubernetes.io/name: {{ include "marketpulse.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version | replace "+" "_" }}
{{- end -}}

{{- define "marketpulse.componentLabels" -}}
{{ include "marketpulse.labels" .root }}
app.kubernetes.io/component: {{ .component }}
{{- end -}}

{{- define "marketpulse.secretName" -}}
{{- if .Values.secrets.create -}}
{{- include "marketpulse.fullname" . -}}-secrets
{{- else -}}
{{- required "secrets.existingSecret is required when secrets.create=false" .Values.secrets.existingSecret -}}
{{- end -}}
{{- end -}}
