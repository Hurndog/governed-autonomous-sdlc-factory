// apps/web/src/lib/mock-data.ts
// Comprehensive mock data for the SDLC Factory command center

// ─── Application ──────────────────────────────────────────────────────
export const mockApplication = {
  id: 'app-001',
  name: 'PaymentHub',
  description: 'Enterprise payment processing platform with multi-gateway support, fraud detection, and real-time reconciliation.',
  status: 'building' as const,
  createdAt: '2026-05-10T08:00:00Z',
  updatedAt: '2026-05-14T07:30:00Z',
  repository: 'github.com/acme/paymenthub',
  primaryLanguage: 'TypeScript',
  framework: 'Next.js + FastAPI',
};

// ─── Build Run ────────────────────────────────────────────────────────
export const mockBuildRun = {
  id: 'run-7ff8a2fd',
  applicationId: 'app-001',
  status: 'active' as const,
  phase: 'semantic-coverage' as const,
  startedAt: '2026-05-14T06:00:00Z',
  intent: 'Build PaymentHub v1.0 — full SDLC from specification to release candidate',
  progress: 0.72,
  currentPhase: 9,
  totalPhases: 14,
};

// ─── SDLC Phases ──────────────────────────────────────────────────────
export type PhaseStatus = 'completed' | 'active' | 'pending' | 'blocked' | 'failed';

export interface SDLCPhase {
  id: string;
  name: string;
  shortName: string;
  status: PhaseStatus;
  progress: number;
  completedArtifacts: number;
  totalArtifacts: number;
  failedChecks: number;
  activeAgents: number;
  tokenUsage: number;
  elapsedMinutes: number;
  humanInterventions: number;
  order: number;
}

export const mockPhases: SDLCPhase[] = [
  { id: 'phase-intake', name: 'Intake', shortName: 'Intake', status: 'completed', progress: 1, completedArtifacts: 3, totalArtifacts: 3, failedChecks: 0, activeAgents: 0, tokenUsage: 4200, elapsedMinutes: 12, humanInterventions: 0, order: 1 },
  { id: 'phase-spec', name: 'Specification', shortName: 'Spec', status: 'completed', progress: 1, completedArtifacts: 5, totalArtifacts: 5, failedChecks: 0, activeAgents: 0, tokenUsage: 12800, elapsedMinutes: 28, humanInterventions: 1, order: 2 },
  { id: 'phase-req', name: 'Requirements', shortName: 'Reqs', status: 'completed', progress: 1, completedArtifacts: 8, totalArtifacts: 8, failedChecks: 0, activeAgents: 0, tokenUsage: 18400, elapsedMinutes: 35, humanInterventions: 0, order: 3 },
  { id: 'phase-arch', name: 'Architecture', shortName: 'Arch', status: 'completed', progress: 1, completedArtifacts: 12, totalArtifacts: 12, failedChecks: 1, activeAgents: 0, tokenUsage: 34200, elapsedMinutes: 52, humanInterventions: 2, order: 4 },
  { id: 'phase-gov-design', name: 'Governance Design', shortName: 'Gov', status: 'completed', progress: 1, completedArtifacts: 6, totalArtifacts: 6, failedChecks: 0, activeAgents: 0, tokenUsage: 8600, elapsedMinutes: 18, humanInterventions: 0, order: 5 },
  { id: 'phase-impl', name: 'Implementation', shortName: 'Impl', status: 'completed', progress: 1, completedArtifacts: 24, totalArtifacts: 24, failedChecks: 2, activeAgents: 0, tokenUsage: 68400, elapsedMinutes: 85, humanInterventions: 1, order: 6 },
  { id: 'phase-test-gen', name: 'Test Generation', shortName: 'Tests', status: 'completed', progress: 1, completedArtifacts: 18, totalArtifacts: 18, failedChecks: 0, activeAgents: 0, tokenUsage: 22100, elapsedMinutes: 32, humanInterventions: 0, order: 7 },
  { id: 'phase-sem-cov', name: 'Semantic Coverage', shortName: 'SemCov', status: 'active', progress: 0.65, completedArtifacts: 8, totalArtifacts: 12, failedChecks: 1, activeAgents: 3, tokenUsage: 15800, elapsedMinutes: 22, humanInterventions: 0, order: 8 },
  { id: 'phase-test-align', name: 'Test Alignment', shortName: 'Align', status: 'pending', progress: 0, completedArtifacts: 0, totalArtifacts: 8, failedChecks: 0, activeAgents: 0, tokenUsage: 0, elapsedMinutes: 0, humanInterventions: 0, order: 9 },
  { id: 'phase-sec-review', name: 'Security Review', shortName: 'Sec', status: 'pending', progress: 0, completedArtifacts: 0, totalArtifacts: 6, failedChecks: 0, activeAgents: 0, tokenUsage: 0, elapsedMinutes: 0, humanInterventions: 0, order: 10 },
  { id: 'phase-release-gate', name: 'Release Gate', shortName: 'Gate', status: 'pending', progress: 0, completedArtifacts: 0, totalArtifacts: 4, failedChecks: 0, activeAgents: 0, tokenUsage: 0, elapsedMinutes: 0, humanInterventions: 0, order: 11 },
  { id: 'phase-deploy', name: 'Deployment', shortName: 'Deploy', status: 'pending', progress: 0, completedArtifacts: 0, totalArtifacts: 5, failedChecks: 0, activeAgents: 0, tokenUsage: 0, elapsedMinutes: 0, humanInterventions: 0, order: 12 },
  { id: 'phase-runtime-evidence', name: 'Runtime Evidence', shortName: 'Runtime', status: 'pending', progress: 0, completedArtifacts: 0, totalArtifacts: 3, failedChecks: 0, activeAgents: 0, tokenUsage: 0, elapsedMinutes: 0, humanInterventions: 0, order: 13 },
  { id: 'phase-retrospective', name: 'Retrospective Learning', shortName: 'Retro', status: 'pending', progress: 0, completedArtifacts: 0, totalArtifacts: 2, failedChecks: 0, activeAgents: 0, tokenUsage: 0, elapsedMinutes: 0, humanInterventions: 0, order: 14 },
];

// ─── Agents ───────────────────────────────────────────────────────────
export type AgentStatus = 'idle' | 'working' | 'waiting' | 'error' | 'paused';

export interface Agent {
  id: string;
  name: string;
  role: string;
  status: AgentStatus;
  currentTask: string;
  inputArtifact: string;
  outputArtifact: string;
  confidence: number;
  tokenUsage: number;
  latencyMs: number;
  retryCount: number;
  errorCount: number;
  policyConstraints: string[];
  lastAction: string;
  lastActionAt: string;
  color: string;
}

export const mockAgents: Agent[] = [
  { id: 'agent-product', name: 'Product Analyst', role: 'product-analyst', status: 'idle', currentTask: 'Awaiting next run', inputArtifact: 'User intent', outputArtifact: 'Product spec', confidence: 0.92, tokenUsage: 4200, latencyMs: 1200, retryCount: 0, errorCount: 0, policyConstraints: [], lastAction: 'Completed product analysis', lastActionAt: '2026-05-14T06:12:00Z', color: '#60a5fa' },
  { id: 'agent-req-norm', name: 'Requirement Normalizer', role: 'req-normalizer', status: 'idle', currentTask: 'Awaiting next run', inputArtifact: 'Raw requirements', outputArtifact: 'Normalized requirements', confidence: 0.88, tokenUsage: 18400, latencyMs: 2100, retryCount: 1, errorCount: 0, policyConstraints: ['no-ambiguity'], lastAction: 'Normalized 8 requirements', lastActionAt: '2026-05-14T06:47:00Z', color: '#34d399' },
  { id: 'agent-arch', name: 'Architecture Agent', role: 'architect', status: 'idle', currentTask: 'Awaiting next run', inputArtifact: 'Normalized requirements', outputArtifact: 'Architecture model', confidence: 0.85, tokenUsage: 34200, latencyMs: 3400, retryCount: 2, errorCount: 1, policyConstraints: ['layering', 'security-boundaries'], lastAction: 'Generated architecture v3', lastActionAt: '2026-05-14T07:39:00Z', color: '#fbbf24' },
  { id: 'agent-gov', name: 'Governance Agent', role: 'governance', status: 'idle', currentTask: 'Awaiting next run', inputArtifact: 'Architecture model', outputArtifact: 'Policy framework', confidence: 0.95, tokenUsage: 8600, latencyMs: 800, retryCount: 0, errorCount: 0, policyConstraints: [], lastAction: 'Validated governance framework', lastActionAt: '2026-05-14T06:57:00Z', color: '#a78bfa' },
  { id: 'agent-code', name: 'Code Generation Agent', role: 'code-gen', status: 'idle', currentTask: 'Awaiting next run', inputArtifact: 'Architecture + requirements', outputArtifact: 'Source code', confidence: 0.78, tokenUsage: 68400, latencyMs: 5200, retryCount: 3, errorCount: 2, policyConstraints: ['no-secrets', 'type-safety'], lastAction: 'Generated 24 code artifacts', lastActionAt: '2026-05-14T07:22:00Z', color: '#22d3ee' },
  { id: 'agent-test', name: 'Test Generation Agent', role: 'test-gen', status: 'idle', currentTask: 'Awaiting next run', inputArtifact: 'Code + requirements', outputArtifact: 'Test suite', confidence: 0.82, tokenUsage: 22100, latencyMs: 2800, retryCount: 0, errorCount: 0, policyConstraints: ['coverage-threshold'], lastAction: 'Generated 18 test cases', lastActionAt: '2026-05-14T07:54:00Z', color: '#c084fc' },
  { id: 'agent-sem-cov', name: 'Semantic Coverage Agent', role: 'semantic-cov', status: 'working', currentTask: 'Evaluating test obligation coverage for REQ-005', inputArtifact: 'Test suite + requirements', outputArtifact: 'Coverage report', confidence: 0.72, tokenUsage: 12400, latencyMs: 1800, retryCount: 1, errorCount: 0, policyConstraints: ['semantic-threshold'], lastAction: 'Scored REQ-004 coverage: 0.82', lastActionAt: '2026-05-14T08:14:00Z', color: '#fb923c' },
  { id: 'agent-verifier', name: 'Verifier Agent', role: 'verifier', status: 'working', currentTask: 'Critiquing test assertions for REQ-003', inputArtifact: 'Test cases', outputArtifact: 'Verifier critique', confidence: 0.68, tokenUsage: 3400, latencyMs: 900, retryCount: 0, errorCount: 0, policyConstraints: ['independence'], lastAction: 'Flagged shallow test: test_payment_happy_path', lastActionAt: '2026-05-14T08:13:00Z', color: '#f87171' },
  { id: 'agent-security', name: 'Security Agent', role: 'security', status: 'waiting', currentTask: 'Queued for security review', inputArtifact: 'Source code', outputArtifact: 'Security report', confidence: 0, tokenUsage: 0, latencyMs: 0, retryCount: 0, errorCount: 0, policyConstraints: ['owasp-top-10'], lastAction: 'Waiting for implementation phase', lastActionAt: '2026-05-14T06:00:00Z', color: '#e879f9' },
  { id: 'agent-refactor', name: 'Refactoring Agent', role: 'refactor', status: 'idle', currentTask: 'Awaiting next run', inputArtifact: 'Code + critique', outputArtifact: 'Refactored code', confidence: 0, tokenUsage: 0, latencyMs: 0, retryCount: 0, errorCount: 0, policyConstraints: ['no-behavior-change'], lastAction: 'Not yet activated', lastActionAt: '2026-05-14T06:00:00Z', color: '#38bdf8' },
  { id: 'agent-docs', name: 'Documentation Agent', role: 'docs', status: 'idle', currentTask: 'Awaiting next run', inputArtifact: 'Code + architecture', outputArtifact: 'Documentation', confidence: 0, tokenUsage: 0, latencyMs: 0, retryCount: 0, errorCount: 0, policyConstraints: [], lastAction: 'Not yet activated', lastActionAt: '2026-05-14T06:00:00Z', color: '#a3e635' },
  { id: 'agent-release', name: 'Release Manager', role: 'release-mgr', status: 'idle', currentTask: 'Awaiting next run', inputArtifact: 'All artifacts', outputArtifact: 'Release package', confidence: 0, tokenUsage: 0, latencyMs: 0, retryCount: 0, errorCount: 0, policyConstraints: ['all-gates-pass'], lastAction: 'Not yet activated', lastActionAt: '2026-05-14T06:00:00Z', color: '#f472b6' },
  { id: 'agent-evidence', name: 'Evidence Agent', role: 'evidence', status: 'working', currentTask: 'Binding runtime evidence to REQ-002', inputArtifact: 'Runtime traces', outputArtifact: 'Evidence bindings', confidence: 0.91, tokenUsage: 1200, latencyMs: 400, retryCount: 0, errorCount: 0, policyConstraints: ['immutability'], lastAction: 'Bound 3 evidence items', lastActionAt: '2026-05-14T08:14:00Z', color: '#2dd4bf' },
];

// ─── Requirements ─────────────────────────────────────────────────────
export type RequirementStatus = 'accepted' | 'tested' | 'verified' | 'blocked' | 'weak' | 'pending';

export interface Requirement {
  id: string;
  normalizedStatement: string;
  sourceText: string;
  actor: string;
  action: string;
  object: string;
  criticality: 'critical' | 'high' | 'medium' | 'low';
  securityRelevance: boolean;
  governanceRelevance: boolean;
  ambiguityScore: number;
  testabilityScore: number;
  status: RequirementStatus;
  semanticCoverageScore: number;
  acceptanceCriteriaCount: number;
  testsCount: number;
  negativeTestsCount: number;
}

export const mockRequirements: Requirement[] = [
  { id: 'REQ-001', normalizedStatement: 'The system SHALL process payments through multiple gateway providers', sourceText: 'The system should be able to process payments through multiple gateways', actor: 'System', action: 'process', object: 'payments', criticality: 'critical', securityRelevance: true, governanceRelevance: true, ambiguityScore: 0.1, testabilityScore: 0.95, status: 'verified', semanticCoverageScore: 0.92, acceptanceCriteriaCount: 3, testsCount: 5, negativeTestsCount: 2 },
  { id: 'REQ-002', normalizedStatement: 'The system SHALL validate payment amounts against account balance', sourceText: 'Payment amounts must be validated against the account balance', actor: 'System', action: 'validate', object: 'payment amounts', criticality: 'critical', securityRelevance: true, governanceRelevance: true, ambiguityScore: 0.05, testabilityScore: 0.98, status: 'verified', semanticCoverageScore: 0.88, acceptanceCriteriaCount: 2, testsCount: 4, negativeTestsCount: 2 },
  { id: 'REQ-003', normalizedStatement: 'The system SHALL generate real-time reconciliation reports', sourceText: 'Real-time reconciliation reports should be generated', actor: 'System', action: 'generate', object: 'reconciliation reports', criticality: 'high', securityRelevance: false, governanceRelevance: true, ambiguityScore: 0.2, testabilityScore: 0.75, status: 'tested', semanticCoverageScore: 0.71, acceptanceCriteriaCount: 2, testsCount: 3, negativeTestsCount: 1 },
  { id: 'REQ-004', normalizedStatement: 'The system SHALL enforce role-based access control on all financial operations', sourceText: 'All financial operations must have RBAC', actor: 'System', action: 'enforce', object: 'RBAC', criticality: 'critical', securityRelevance: true, governanceRelevance: true, ambiguityScore: 0.08, testabilityScore: 0.9, status: 'verified', semanticCoverageScore: 0.85, acceptanceCriteriaCount: 4, testsCount: 6, negativeTestsCount: 3 },
  { id: 'REQ-005', normalizedStatement: 'The system SHALL detect and flag suspicious transactions using ML models', sourceText: 'Suspicious transactions should be detected and flagged', actor: 'System', action: 'detect and flag', object: 'suspicious transactions', criticality: 'high', securityRelevance: true, governanceRelevance: true, ambiguityScore: 0.35, testabilityScore: 0.55, status: 'weak', semanticCoverageScore: 0.42, acceptanceCriteriaCount: 2, testsCount: 2, negativeTestsCount: 0 },
  { id: 'REQ-006', normalizedStatement: 'The system SHALL maintain audit logs for all transactions', sourceText: 'All transactions must be audit logged', actor: 'System', action: 'maintain', object: 'audit logs', criticality: 'high', securityRelevance: true, governanceRelevance: true, ambiguityScore: 0.05, testabilityScore: 0.95, status: 'verified', semanticCoverageScore: 0.9, acceptanceCriteriaCount: 2, testsCount: 4, negativeTestsCount: 1 },
  { id: 'REQ-007', normalizedStatement: 'The system SHALL support webhook notifications for payment events', sourceText: 'Webhook notifications for payment events', actor: 'System', action: 'support', object: 'webhook notifications', criticality: 'medium', securityRelevance: false, governanceRelevance: false, ambiguityScore: 0.15, testabilityScore: 0.8, status: 'tested', semanticCoverageScore: 0.68, acceptanceCriteriaCount: 2, testsCount: 3, negativeTestsCount: 1 },
  { id: 'REQ-008', normalizedStatement: 'The system SHALL provide a dashboard for transaction monitoring', sourceText: 'A dashboard for transaction monitoring should be available', actor: 'System', action: 'provide', object: 'monitoring dashboard', criticality: 'medium', securityRelevance: false, governanceRelevance: false, ambiguityScore: 0.25, testabilityScore: 0.6, status: 'pending', semanticCoverageScore: 0.35, acceptanceCriteriaCount: 1, testsCount: 1, negativeTestsCount: 0 },
];

// ─── Token Usage ──────────────────────────────────────────────────────
export const mockTokenUsage = {
  totalTokens: 174100,
  inputTokens: 98200,
  outputTokens: 62400,
  cachedTokens: 8500,
  reasoningTokens: 5000,
  totalCostUsd: 1.847,
  budgetTotal: 5.0,
  budgetRemaining: 3.153,
  byPhase: [
    { phase: 'Intake', tokens: 4200, cost: 0.042 },
    { phase: 'Specification', tokens: 12800, cost: 0.128 },
    { phase: 'Requirements', tokens: 18400, cost: 0.184 },
    { phase: 'Architecture', tokens: 34200, cost: 0.342 },
    { phase: 'Governance', tokens: 8600, cost: 0.086 },
    { phase: 'Implementation', tokens: 68400, cost: 0.684 },
    { phase: 'Test Generation', tokens: 22100, cost: 0.221 },
    { phase: 'Semantic Coverage', tokens: 15800, cost: 0.158 },
  ],
  byAgent: [
    { agent: 'Code Generation', tokens: 68400, cost: 0.684 },
    { agent: 'Architecture', tokens: 34200, cost: 0.342 },
    { agent: 'Test Generation', tokens: 22100, cost: 0.221 },
    { agent: 'Requirements', tokens: 18400, cost: 0.184 },
    { agent: 'Semantic Coverage', tokens: 15800, cost: 0.158 },
    { agent: 'Specification', tokens: 12800, cost: 0.128 },
    { agent: 'Governance', tokens: 8600, cost: 0.086 },
    { agent: 'Intake', tokens: 4200, cost: 0.042 },
  ],
  burnRate: [
    { time: '06:00', tokens: 0 },
    { time: '06:15', tokens: 4200 },
    { time: '06:30', tokens: 17000 },
    { time: '06:45', tokens: 35400 },
    { time: '07:00', tokens: 44000 },
    { time: '07:15', tokens: 112400 },
    { time: '07:30', tokens: 134500 },
    { time: '07:45', tokens: 156600 },
    { time: '08:00', tokens: 170100 },
    { time: '08:15', tokens: 174100 },
  ],
  wastedTokens: {
    total: 28400,
    byCategory: [
      { category: 'Repeated regeneration', tokens: 12800, reason: 'Architecture Agent regenerated integration model 3 times due to API ambiguity' },
      { category: 'Failed tests', tokens: 6200, reason: 'Code Generation produced code that failed initial test run' },
      { category: 'Governance rejections', tokens: 4800, reason: 'Security policy violations required rework' },
      { category: 'Poor context selection', tokens: 2800, reason: 'Agent included irrelevant files in context window' },
      { category: 'Excessive agent chatter', tokens: 1800, reason: 'Unnecessary inter-agent communication overhead' },
    ],
  },
  costPerAcceptedRequirement: 0.231,
  costPerPassingTest: 0.103,
  costPerSemanticallyCoveredReq: 0.289,
  costPerReleaseCandidate: 1.847,
};

// ─── Semantic Coverage ────────────────────────────────────────────────
export const mockSemanticCoverage = {
  overallScore: 0.6559,
  obligationCoverage: 0.72,
  semanticAlignment: 0.68,
  mutationScore: 0.58,
  negativeCoverage: 0.63,
  runtimeEvidence: 0.71,
  verifierConfidence: 0.66,
  criticalRequirementsPassed: false,
  releaseGateStatus: 'failed',
  falseConfidenceTests: [
    { testId: 'test-payment-happy', name: 'test_payment_happy_path', issue: 'Only tests happy path, no boundary validation', requirementId: 'REQ-001', severity: 'high' },
    { testId: 'test-auth-check', name: 'test_auth_check_exists', issue: 'Checks function existence, not authorization logic', requirementId: 'REQ-004', severity: 'critical' },
    { testId: 'test-reconciliation', name: 'test_reconciliation_runs', issue: 'Verifies report generation, not data accuracy', requirementId: 'REQ-003', severity: 'medium' },
  ],
  coverageMatrix: [
    { requirementId: 'REQ-001', unitTest: 'covered', integrationTest: 'covered', contractTest: 'covered', e2eTest: 'partial', negativeTest: 'covered', mutationTest: 'covered', runtimeEvidence: 'covered', verifierApproval: 'approved' },
    { requirementId: 'REQ-002', unitTest: 'covered', integrationTest: 'covered', contractTest: 'covered', e2eTest: 'covered', negativeTest: 'covered', mutationTest: 'covered', runtimeEvidence: 'covered', verifierApproval: 'approved' },
    { requirementId: 'REQ-003', unitTest: 'covered', integrationTest: 'partial', contractTest: 'missing', e2eTest: 'partial', negativeTest: 'covered', mutationTest: 'partial', runtimeEvidence: 'covered', verifierApproval: 'approved' },
    { requirementId: 'REQ-004', unitTest: 'covered', integrationTest: 'covered', contractTest: 'covered', e2eTest: 'covered', negativeTest: 'covered', mutationTest: 'covered', runtimeEvidence: 'covered', verifierApproval: 'flagged' },
    { requirementId: 'REQ-005', unitTest: 'partial', integrationTest: 'missing', contractTest: 'missing', e2eTest: 'missing', negativeTest: 'missing', mutationTest: 'missing', runtimeEvidence: 'partial', verifierApproval: 'rejected' },
    { requirementId: 'REQ-006', unitTest: 'covered', integrationTest: 'covered', contractTest: 'covered', e2eTest: 'covered', negativeTest: 'covered', mutationTest: 'covered', runtimeEvidence: 'covered', verifierApproval: 'approved' },
    { requirementId: 'REQ-007', unitTest: 'covered', integrationTest: 'covered', contractTest: 'partial', e2eTest: 'partial', negativeTest: 'covered', mutationTest: 'partial', runtimeEvidence: 'covered', verifierApproval: 'approved' },
    { requirementId: 'REQ-008', unitTest: 'partial', integrationTest: 'missing', contractTest: 'missing', e2eTest: 'missing', negativeTest: 'missing', mutationTest: 'missing', runtimeEvidence: 'missing', verifierApproval: 'pending' },
  ],
};

// ─── Architecture ─────────────────────────────────────────────────────
export interface ArchComponent {
  id: string;
  name: string;
  type: 'service' | 'api' | 'database' | 'frontend' | 'integration' | 'queue' | 'cache';
  status: 'implemented' | 'generated' | 'tested' | 'verified' | 'blocked' | 'pending';
  dependencies: string[];
  tokenCost: number;
  changeFrequency: number;
  testCoverage: number;
}

export const mockArchComponents: ArchComponent[] = [
  { id: 'comp-api-gateway', name: 'API Gateway', type: 'api', status: 'verified', dependencies: [], tokenCost: 4200, changeFrequency: 1, testCoverage: 0.95 },
  { id: 'comp-auth-svc', name: 'Auth Service', type: 'service', status: 'verified', dependencies: ['comp-user-db'], tokenCost: 6800, changeFrequency: 2, testCoverage: 0.92 },
  { id: 'comp-payment-svc', name: 'Payment Service', type: 'service', status: 'tested', dependencies: ['comp-api-gateway', 'comp-fraud-svc', 'comp-ledger-db'], tokenCost: 12400, changeFrequency: 3, testCoverage: 0.78 },
  { id: 'comp-fraud-svc', name: 'Fraud Detection', type: 'service', status: 'generated', dependencies: ['comp-ml-model', 'comp-transaction-queue'], tokenCost: 8600, changeFrequency: 4, testCoverage: 0.45 },
  { id: 'comp-reconciliation-svc', name: 'Reconciliation', type: 'service', status: 'tested', dependencies: ['comp-ledger-db', 'comp-payment-svc'], tokenCost: 5200, changeFrequency: 1, testCoverage: 0.72 },
  { id: 'comp-webhook-svc', name: 'Webhook Service', type: 'service', status: 'tested', dependencies: ['comp-transaction-queue'], tokenCost: 3800, changeFrequency: 1, testCoverage: 0.81 },
  { id: 'comp-dashboard', name: 'Dashboard UI', type: 'frontend', status: 'generated', dependencies: ['comp-api-gateway'], tokenCost: 4600, changeFrequency: 2, testCoverage: 0.35 },
  { id: 'comp-user-db', name: 'User Database', type: 'database', status: 'verified', dependencies: [], tokenCost: 1200, changeFrequency: 0, testCoverage: 1.0 },
  { id: 'comp-ledger-db', name: 'Ledger Database', type: 'database', status: 'verified', dependencies: [], tokenCost: 1400, changeFrequency: 0, testCoverage: 1.0 },
  { id: 'comp-transaction-queue', name: 'Transaction Queue', type: 'queue', status: 'verified', dependencies: [], tokenCost: 2200, changeFrequency: 0, testCoverage: 0.88 },
  { id: 'comp-ml-model', name: 'ML Model', type: 'integration', status: 'blocked', dependencies: [], tokenCost: 3200, changeFrequency: 5, testCoverage: 0.15 },
  { id: 'comp-notification-cache', name: 'Notification Cache', type: 'cache', status: 'verified', dependencies: [], tokenCost: 800, changeFrequency: 0, testCoverage: 0.9 },
];

export const mockADRs = [
  { id: 'ADR-001', title: 'Use event-driven architecture for payment processing', context: 'Payment processing requires async handling for reliability', decision: 'Event-driven with transaction queue', status: 'accepted', consequences: 'Better resilience, added complexity', linkedRequirements: ['REQ-001', 'REQ-003'] },
  { id: 'ADR-002', title: 'Separate fraud detection into independent service', context: 'Fraud detection has different scaling and model update requirements', decision: 'Independent microservice with own model registry', status: 'accepted', consequences: 'Independent deployment, network latency', linkedRequirements: ['REQ-005'] },
  { id: 'ADR-003', title: 'RBAC at API gateway level', context: 'Need consistent auth enforcement across all services', decision: 'Centralized RBAC at gateway with service-level enforcement', status: 'accepted', consequences: 'Single point of auth, consistent policy', linkedRequirements: ['REQ-004'] },
  { id: 'ADR-004', title: 'Use PostgreSQL for ledger with append-only pattern', context: 'Financial data requires audit trail and immutability', decision: 'Append-only ledger table with hash chain', status: 'accepted', consequences: 'Immutable audit trail, larger storage', linkedRequirements: ['REQ-002', 'REQ-006'] },
];

export const mockArchDrift = [
  { domain: 'Layering', score: 0.15, status: 'ok' },
  { domain: 'Dependency Direction', score: 0.22, status: 'ok' },
  { domain: 'Naming Conventions', score: 0.08, status: 'ok' },
  { domain: 'API Contract Compliance', score: 0.35, status: 'warning' },
  { domain: 'Security Boundaries', score: 0.12, status: 'ok' },
  { domain: 'Data Ownership', score: 0.18, status: 'ok' },
  { domain: 'Observability', score: 0.42, status: 'warning' },
  { domain: 'Deployment Topology', score: 0.28, status: 'ok' },
];

// ─── Governance ───────────────────────────────────────────────────────
export interface GovGate {
  id: string;
  name: string;
  status: 'passed' | 'failed' | 'pending' | 'waived' | 'escalated' | 'blocked';
  owner: string;
  timestamp: string;
  policyBasis: string;
  impact: 'critical' | 'high' | 'medium' | 'low';
  evidence: string[];
}

export const mockGovGates: GovGate[] = [
  { id: 'gate-req-approval', name: 'Requirement Approval', status: 'passed', owner: 'Product Analyst', timestamp: '2026-05-14T06:47:00Z', policyBasis: 'All requirements must be normalized and unambiguous', impact: 'critical', evidence: ['REQ-001', 'REQ-002', 'REQ-003'] },
  { id: 'gate-arch-approval', name: 'Architecture Approval', status: 'passed', owner: 'Architecture Agent', timestamp: '2026-05-14T07:39:00Z', policyBasis: 'Architecture must satisfy all critical requirements', impact: 'critical', evidence: ['ADR-001', 'ADR-002', 'ADR-003'] },
  { id: 'gate-data-access', name: 'Data Access Approval', status: 'passed', owner: 'Governance Agent', timestamp: '2026-05-14T06:57:00Z', policyBasis: 'Data access patterns must comply with governance policy', impact: 'high', evidence: ['ADR-004'] },
  { id: 'gate-security', name: 'Security Approval', status: 'pending', owner: 'Security Agent', timestamp: '', policyBasis: 'OWASP Top 10 compliance required', impact: 'critical', evidence: [] },
  { id: 'gate-test-adequacy', name: 'Test Adequacy Approval', status: 'failed', owner: 'Verifier Agent', timestamp: '2026-05-14T08:13:00Z', policyBasis: 'All critical requirements must have passing tests', impact: 'critical', evidence: ['REQ-005-false-confidence'] },
  { id: 'gate-semantic-cov', name: 'Semantic Coverage Approval', status: 'failed', owner: 'Semantic Coverage Agent', timestamp: '2026-05-14T08:14:00Z', policyBasis: 'Semantic coverage score must exceed 0.8', impact: 'critical', evidence: ['coverage-report-001'] },
  { id: 'gate-compliance', name: 'Compliance Approval', status: 'pending', owner: 'Governance Agent', timestamp: '', policyBasis: 'All governance policies must be satisfied', impact: 'high', evidence: [] },
  { id: 'gate-release', name: 'Release Approval', status: 'blocked', owner: 'Release Manager', timestamp: '', policyBasis: 'All gates must pass before release', impact: 'critical', evidence: [] },
  { id: 'gate-deploy', name: 'Deployment Approval', status: 'blocked', owner: 'Release Manager', timestamp: '', policyBasis: 'Release gate must pass before deployment', impact: 'critical', evidence: [] },
];

// ─── Process Events ───────────────────────────────────────────────────
export interface ProcessEvent {
  id: string;
  timestamp: string;
  agent: string;
  action: string;
  artifact: string;
  tokenCost: number;
  result: 'success' | 'failure' | 'warning' | 'info';
  phase: string;
}

export const mockProcessEvents: ProcessEvent[] = [
  { id: 'evt-001', timestamp: '2026-05-14T06:00:00Z', agent: 'Product Analyst', action: 'Analyzed user intent', artifact: 'product-spec-v1', tokenCost: 4200, result: 'success', phase: 'Intake' },
  { id: 'evt-002', timestamp: '2026-05-14T06:12:00Z', agent: 'Requirement Normalizer', action: 'Normalized requirements', artifact: 'normalized-reqs-v1', tokenCost: 8400, result: 'success', phase: 'Specification' },
  { id: 'evt-003', timestamp: '2026-05-14T06:28:00Z', agent: 'Requirement Normalizer', action: 'Regenerated requirements (ambiguity)', artifact: 'normalized-reqs-v2', tokenCost: 10000, result: 'warning', phase: 'Specification' },
  { id: 'evt-004', timestamp: '2026-05-14T06:47:00Z', agent: 'Architecture Agent', action: 'Generated architecture v1', artifact: 'arch-v1', tokenCost: 12000, result: 'success', phase: 'Architecture' },
  { id: 'evt-005', timestamp: '2026-05-14T07:05:00Z', agent: 'Architecture Agent', action: 'Regenerated architecture (API conflict)', artifact: 'arch-v2', tokenCost: 11000, result: 'warning', phase: 'Architecture' },
  { id: 'evt-006', timestamp: '2026-05-14T07:22:00Z', agent: 'Architecture Agent', action: 'Regenerated architecture (resolved)', artifact: 'arch-v3', tokenCost: 11200, result: 'success', phase: 'Architecture' },
  { id: 'evt-007', timestamp: '2026-05-14T07:39:00Z', agent: 'Code Generation', action: 'Generated payment service', artifact: 'payment-svc-v1', tokenCost: 18400, result: 'success', phase: 'Implementation' },
  { id: 'evt-008', timestamp: '2026-05-14T07:45:00Z', agent: 'Code Generation', action: 'Generated fraud service', artifact: 'fraud-svc-v1', tokenCost: 16200, result: 'failure', phase: 'Implementation' },
  { id: 'evt-009', timestamp: '2026-05-14T07:48:00Z', agent: 'Code Generation', action: 'Regenerated fraud service', artifact: 'fraud-svc-v2', tokenCost: 15800, result: 'success', phase: 'Implementation' },
  { id: 'evt-010', timestamp: '2026-05-14T07:54:00Z', agent: 'Test Generation', action: 'Generated test suite', artifact: 'test-suite-v1', tokenCost: 22100, result: 'success', phase: 'Test Generation' },
  { id: 'evt-011', timestamp: '2026-05-14T08:05:00Z', agent: 'Semantic Coverage', action: 'Evaluated REQ-001 coverage', artifact: 'sem-cov-001', tokenCost: 3200, result: 'success', phase: 'Semantic Coverage' },
  { id: 'evt-012', timestamp: '2026-05-14T08:10:00Z', agent: 'Semantic Coverage', action: 'Evaluated REQ-005 coverage', artifact: 'sem-cov-005', tokenCost: 4800, result: 'warning', phase: 'Semantic Coverage' },
  { id: 'evt-013', timestamp: '2026-05-14T08:13:00Z', agent: 'Verifier', action: 'Flagged false confidence test', artifact: 'verifier-report-001', tokenCost: 2200, result: 'warning', phase: 'Semantic Coverage' },
  { id: 'evt-014', timestamp: '2026-05-14T08:14:00Z', agent: 'Evidence Agent', action: 'Bound runtime evidence', artifact: 'evidence-binding-002', tokenCost: 1200, result: 'success', phase: 'Semantic Coverage' },
];

// ─── Backlog Items ────────────────────────────────────────────────────
export interface BacklogItem {
  id: string;
  title: string;
  type: 'feature' | 'component' | 'screen' | 'api' | 'database' | 'integration' | 'test' | 'policy' | 'documentation';
  status: 'accepted' | 'tested' | 'verified' | 'blocked' | 'in-progress' | 'pending';
  owner: string;
  phase: string;
  dependencies: string[];
  risk: 'critical' | 'high' | 'medium' | 'low';
  tokenCost: number;
  releaseImpact: 'critical' | 'high' | 'medium' | 'low';
  checked: boolean;
}

export const mockBacklog: BacklogItem[] = [
  { id: 'bl-001', title: 'Payment Gateway Integration', type: 'feature', status: 'verified', owner: 'Code Generation', phase: 'Implementation', dependencies: [], risk: 'critical', tokenCost: 18400, releaseImpact: 'critical', checked: true },
  { id: 'bl-002', title: 'Fraud Detection Service', type: 'component', status: 'blocked', owner: 'Code Generation', phase: 'Implementation', dependencies: ['ML Model'], risk: 'high', tokenCost: 16200, releaseImpact: 'high', checked: false },
  { id: 'bl-003', title: 'RBAC System', type: 'feature', status: 'verified', owner: 'Code Generation', phase: 'Implementation', dependencies: ['User Database'], risk: 'critical', tokenCost: 8600, releaseImpact: 'critical', checked: true },
  { id: 'bl-004', title: 'Reconciliation Engine', type: 'component', status: 'tested', owner: 'Code Generation', phase: 'Implementation', dependencies: ['Ledger Database'], risk: 'high', tokenCost: 5200, releaseImpact: 'high', checked: true },
  { id: 'bl-005', title: 'Webhook Notification System', type: 'component', status: 'tested', owner: 'Code Generation', phase: 'Implementation', dependencies: ['Transaction Queue'], risk: 'medium', tokenCost: 3800, releaseImpact: 'medium', checked: true },
  { id: 'bl-006', title: 'Transaction Dashboard', type: 'screen', status: 'pending', owner: 'Code Generation', phase: 'Implementation', dependencies: ['API Gateway'], risk: 'medium', tokenCost: 4600, releaseImpact: 'medium', checked: false },
  { id: 'bl-007', title: 'Payment API Contract', type: 'api', status: 'verified', owner: 'Architecture', phase: 'Architecture', dependencies: [], risk: 'critical', tokenCost: 4200, releaseImpact: 'critical', checked: true },
  { id: 'bl-008', title: 'Ledger Database Schema', type: 'database', status: 'verified', owner: 'Architecture', phase: 'Architecture', dependencies: [], risk: 'high', tokenCost: 1400, releaseImpact: 'high', checked: true },
  { id: 'bl-009', title: 'Security Policy Framework', type: 'policy', status: 'verified', owner: 'Governance', phase: 'Governance Design', dependencies: [], risk: 'critical', tokenCost: 8600, releaseImpact: 'critical', checked: true },
  { id: 'bl-010', title: 'Negative Test Suite', type: 'test', status: 'in-progress', owner: 'Test Generation', phase: 'Test Generation', dependencies: ['Test Suite'], risk: 'high', tokenCost: 6200, releaseImpact: 'high', checked: false },
  { id: 'bl-011', title: 'Mutation Test Suite', type: 'test', status: 'pending', owner: 'Test Generation', phase: 'Test Generation', dependencies: ['Test Suite'], risk: 'medium', tokenCost: 0, releaseImpact: 'medium', checked: false },
  { id: 'bl-012', title: 'API Documentation', type: 'documentation', status: 'pending', owner: 'Documentation', phase: 'Documentation', dependencies: ['All APIs'], risk: 'low', tokenCost: 0, releaseImpact: 'low', checked: false },
];

// ─── Scores ───────────────────────────────────────────────────────────
export const mockScores = {
  releaseReadiness: 0.62,
  evidenceMaturity: 0.78,
  semanticCoverage: 0.6559,
  architectureDrift: 0.22,
  technicalDebt: 0.28,
  governanceRisk: 0.45,
  integrityScore: 0.9508,
  testCoverage: 0.74,
  overallProgress: 0.72,
  overloadProgress: 0.72,
};

// ─── Human Interventions ──────────────────────────────────────────────
export interface HumanIntervention {
  id: string;
  timestamp: string;
  user: string;
  action: string;
  target: string;
  reason: string;
  resolved: boolean;
}

export const mockHumanInterventions: HumanIntervention[] = [
  { id: 'hi-001', timestamp: '2026-05-14T06:30:00Z', user: 'Marco', action: 'Approved specification', target: 'product-spec-v1', reason: 'Specification looks correct', resolved: true },
  { id: 'hi-002', timestamp: '2026-05-14T07:10:00Z', user: 'Marco', action: 'Requested regeneration', target: 'arch-v1', reason: 'API contract conflict between payment and fraud services', resolved: true },
  { id: 'hi-003', timestamp: '2026-05-14T07:25:00Z', user: 'Marco', action: 'Approved architecture', target: 'arch-v3', reason: 'Architecture resolves all conflicts', resolved: true },
  { id: 'hi-004', timestamp: '2026-05-14T07:50:00Z', user: 'Marco', action: 'Requested regeneration', target: 'fraud-svc-v1', reason: 'Security policy violation in initial implementation', resolved: true },
];
