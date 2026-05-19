'use client';

import React, { useState, useEffect } from 'react';
import { SectionHeader } from '@/components/ui/SectionHeader';
import { StatusChip } from '@/components/ui/StatusChip';
import { DataSourceBadge, DataSourceBanner } from '@/components/ui/DataSourceBadge';
import { useAuthStore } from '@/lib/authStore';
import { api } from '@/lib/api';
import { UserPlus, Shield, UserCog, AlertCircle, CheckCircle2, X } from 'lucide-react';

interface UserItem {
  id: string;
  email: string;
  display_name: string;
  role: string;
  is_active: boolean;
  created_at: string | null;
  last_login_at: string | null;
}

const ROLES = ['admin', 'architect', 'engineer', 'governance_reviewer', 'executive_viewer', 'auditor', 'operator'];

export function UserManagement() {
  const { user: currentUser } = useAuthStore();
  const [users, setUsers] = useState<UserItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dataSource, setDataSource] = useState<'LIVE' | 'ERROR' | 'LOADING'>('LOADING');
  const [showCreate, setShowCreate] = useState(false);
  const [createForm, setCreateForm] = useState({ email: '', display_name: '', password: '', role: 'engineer' });
  const [createError, setCreateError] = useState<string | null>(null);
  const [createLoading, setCreateLoading] = useState(false);
  const [editingUser, setEditingUser] = useState<string | null>(null);
  const [editRole, setEditRole] = useState('');

  const fetchUsers = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'}/users`,
        {
          headers: { Authorization: `Bearer ${useAuthStore.getState().token}` },
        }
      );
      if (!res.ok) throw new Error(`Failed: ${res.status}`);
      const data = await res.json();
      setUsers(data.users || []);
      setDataSource('LIVE');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch users');
      setDataSource('ERROR');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setCreateError(null);
    setCreateLoading(true);
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'}/users`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${useAuthStore.getState().token}`,
          },
          body: JSON.stringify(createForm),
        }
      );
      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.detail || `Failed: ${res.status}`);
      }
      setShowCreate(false);
      setCreateForm({ email: '', display_name: '', password: '', role: 'engineer' });
      fetchUsers();
    } catch (err) {
      setCreateError(err instanceof Error ? err.message : 'Failed to create user');
    } finally {
      setCreateLoading(false);
    }
  };

  const handleRoleChange = async (userId: string, newRole: string) => {
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'}/users/${userId}`,
        {
          method: 'PATCH',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${useAuthStore.getState().token}`,
          },
          body: JSON.stringify({ role: newRole }),
        }
      );
      if (!res.ok) throw new Error(`Failed: ${res.status}`);
      setEditingUser(null);
      fetchUsers();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update role');
    }
  };

  const handleToggleActive = async (userId: string, currentActive: boolean) => {
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'}/users/${userId}`,
        {
          method: 'PATCH',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${useAuthStore.getState().token}`,
          },
          body: JSON.stringify({ is_active: !currentActive }),
        }
      );
      if (!res.ok) throw new Error(`Failed: ${res.status}`);
      fetchUsers();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update user');
    }
  };

  const roleColors: Record<string, string> = {
    admin: 'bg-red-500/10 text-red-400 border-red-500/20',
    architect: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
    engineer: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
    governance_reviewer: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
    executive_viewer: 'bg-violet-500/10 text-violet-400 border-violet-500/20',
    auditor: 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20',
    operator: 'bg-orange-500/10 text-orange-400 border-orange-500/20',
  };

  return (
    <div className="p-6 space-y-4 max-w-[1600px] mx-auto">
      <DataSourceBanner state={dataSource} message={error || undefined} />

      <div className="flex items-center justify-between">
        <SectionHeader title="User Management" subtitle={`${users.length} users`} />
        <div className="flex items-center gap-2">
          <DataSourceBadge state={dataSource} />
          <button
            onClick={() => setShowCreate(!showCreate)}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-blue-600 hover:bg-blue-500 text-white text-[10px] font-medium"
          >
            <UserPlus className="w-3 h-3" />
            Create User
          </button>
        </div>
      </div>

      {/* Create user form */}
      {showCreate && (
        <div className="card p-4">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-xs font-semibold text-zinc-300">Create New User</h3>
            <button onClick={() => setShowCreate(false)} className="text-zinc-500 hover:text-zinc-300">
              <X className="w-4 h-4" />
            </button>
          </div>
          {createError && (
            <div className="flex items-center gap-2 p-2 rounded bg-red-500/10 border border-red-500/20 text-red-400 text-[10px] mb-3">
              <AlertCircle className="w-3 h-3" />
              {createError}
            </div>
          )}
          <form onSubmit={handleCreate} className="grid grid-cols-4 gap-3">
            <div>
              <label className="block text-[9px] uppercase text-zinc-600 mb-1">Email</label>
              <input
                type="email"
                required
                value={createForm.email}
                onChange={(e) => setCreateForm({ ...createForm, email: e.target.value })}
                className="w-full px-2 py-1.5 rounded bg-zinc-800/50 border border-zinc-700/50 text-[11px] text-zinc-200 focus:outline-none focus:border-blue-500/50"
              />
            </div>
            <div>
              <label className="block text-[9px] uppercase text-zinc-600 mb-1">Display Name</label>
              <input
                type="text"
                required
                value={createForm.display_name}
                onChange={(e) => setCreateForm({ ...createForm, display_name: e.target.value })}
                className="w-full px-2 py-1.5 rounded bg-zinc-800/50 border border-zinc-700/50 text-[11px] text-zinc-200 focus:outline-none focus:border-blue-500/50"
              />
            </div>
            <div>
              <label className="block text-[9px] uppercase text-zinc-600 mb-1">Password</label>
              <input
                type="password"
                required
                minLength={8}
                value={createForm.password}
                onChange={(e) => setCreateForm({ ...createForm, password: e.target.value })}
                className="w-full px-2 py-1.5 rounded bg-zinc-800/50 border border-zinc-700/50 text-[11px] text-zinc-200 focus:outline-none focus:border-blue-500/50"
              />
            </div>
            <div>
              <label className="block text-[9px] uppercase text-zinc-600 mb-1">Role</label>
              <select
                value={createForm.role}
                onChange={(e) => setCreateForm({ ...createForm, role: e.target.value })}
                className="w-full px-2 py-1.5 rounded bg-zinc-800/50 border border-zinc-700/50 text-[11px] text-zinc-200 focus:outline-none focus:border-blue-500/50"
              >
                {ROLES.map((r) => (
                  <option key={r} value={r}>{r}</option>
                ))}
              </select>
            </div>
            <div className="col-span-4 flex justify-end">
              <button
                type="submit"
                disabled={createLoading}
                className="px-4 py-1.5 rounded bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white text-[10px] font-medium"
              >
                {createLoading ? 'Creating...' : 'Create User'}
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Users table */}
      <div className="card p-4">
        <div className="space-y-2">
          {users.map((u) => (
            <div
              key={u.id}
              className="flex items-center gap-3 p-3 rounded-lg bg-zinc-800/20 border border-zinc-800/40"
            >
              <div className="w-8 h-8 rounded-full bg-violet-500/20 border border-violet-500/30 flex items-center justify-center">
                <span className="text-[10px] font-bold text-violet-400">
                  {u.display_name.charAt(0).toUpperCase()}
                </span>
              </div>
              <div className="flex-1 min-w-0">
                <div className="text-[11px] font-medium text-zinc-300 truncate">{u.display_name}</div>
                <div className="text-[9px] text-zinc-600">{u.email}</div>
              </div>

              {/* Role */}
              {editingUser === u.id ? (
                <select
                  value={editRole}
                  onChange={(e) => setEditRole(e.target.value)}
                  onBlur={() => { handleRoleChange(u.id, editRole); setEditingUser(null); }}
                  autoFocus
                  className="px-2 py-1 rounded bg-zinc-800/50 border border-zinc-700/50 text-[10px] text-zinc-200"
                >
                  {ROLES.map((r) => (
                    <option key={r} value={r}>{r}</option>
                  ))}
                </select>
              ) : (
                <button
                  onClick={() => { setEditingUser(u.id); setEditRole(u.role); }}
                  className={`px-2 py-0.5 rounded text-[9px] font-medium border ${roleColors[u.role] || 'bg-zinc-500/10 text-zinc-400 border-zinc-500/20'}`}
                >
                  {u.role}
                </button>
              )}

              {/* Active status */}
              <button
                onClick={() => handleToggleActive(u.id, u.is_active)}
                className="flex items-center gap-1"
                title={u.is_active ? 'Active — click to deactivate' : 'Inactive — click to activate'}
              >
                {u.is_active ? (
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                ) : (
                  <AlertCircle className="w-3.5 h-3.5 text-red-400" />
                )}
              </button>

              <span className="text-[9px] text-zinc-600 w-20 text-right">
                {u.last_login_at ? new Date(u.last_login_at).toLocaleDateString() : 'Never'}
              </span>
            </div>
          ))}

          {users.length === 0 && !loading && (
            <div className="text-center py-8 text-zinc-600 text-xs">No users found</div>
          )}
        </div>
      </div>
    </div>
  );
}
