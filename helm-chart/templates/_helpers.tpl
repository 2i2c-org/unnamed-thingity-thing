{{/*
Expand the name of the chart.
*/}}
{{- define "frx-challenges.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "frx-challenges.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "frx-challenges.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "frx-challenges.labels" -}}
helm.sh/chart: {{ include "frx-challenges.chart" . }}
{{ include "frx-challenges.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "frx-challenges.selectorLabels" -}}
app.kubernetes.io/name: {{ include "frx-challenges.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{- define "frx-challenges.toYamlRecursive" -}}
{{- range $key, $value := . }}
  {{- if kindIs "map" $value }}
    {{ $key }}:
{{- include "frx-challenges.toYamlRecursive" $value | indent 2 }}
  {{- else if or (kindIs "array" $value) (kindIs "slice" $value) }}
    {{ $key }}:
{{- range $item := $value }}
      - {{ $item }}
{{- end }}
  {{- else }}
    {{ $key }}: {{ $value }}
  {{- end }}
{{- end }}
{{- end }}
